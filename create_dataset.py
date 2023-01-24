# Simulator classes
from simulator import *

# Python libraries
import random
import networkx as nx
import matplotlib.pyplot as plt


def uniform(n_items: int, valid_values: list, shuffle_distribution: bool = True) -> list:
    """Creates a list of size "n_items" with values from "valid_values" according to the uniform distribution.
    By default, the method shuffles the created list to avoid unbalanced spread of the distribution.
    Args:
        n_items (int): Number of items that will be created.
        valid_values (list): List of valid values for the list of values.
        shuffle_distribution (bool, optional): Defines whether the distribution is shuffled or not. Defaults to True.
    Raises:
        Exception: Invalid "valid_values" argument.
    Returns:
        uniform_distribution (list): List of values arranged according to the uniform distribution.
    """
    if not isinstance(valid_values, list) or isinstance(valid_values, list) and len(valid_values) == 0:
        raise Exception("You must inform a list of valid values within the 'valid_values' attribute.")

    # Number of occurrences that will be created of each item in the "valid_values" list
    distribution = [int(n_items / len(valid_values)) for _ in range(0, len(valid_values))]

    # List with size "n_items" that will be populated with "valid_values" according to the uniform distribution
    uniform_distribution = []

    for i, value in enumerate(valid_values):
        for _ in range(0, int(distribution[i])):
            uniform_distribution.append(value)

    # Computing leftover randomly to avoid disturbing the distribution
    leftover = n_items % len(valid_values)
    for i in range(leftover):
        random_valid_value = random.choice(valid_values)
        uniform_distribution.append(random_valid_value)

    # Shuffling distribution values in case 'shuffle_distribution' parameter is True
    if shuffle_distribution:
        random.shuffle(uniform_distribution)

    return uniform_distribution


def display_topology(topology: object, output_filename: str = "topology"):
    # Customizing visual representation of topology
    positions = {}
    labels = {}
    colors = []
    sizes = []

    for node in topology.nodes():
        positions[node] = node.coordinates
        labels[node] = node.id
        node_size = 500 if any(user.coordinates == node.coordinates for user in User.all()) else 100
        sizes.append(node_size)
        colors.append("black")

    link_widths = [150 * (1 / link_metadata[2]["delay"]) for link_metadata in Topology.first().edges(data=True)]

    # Configuring drawing scheme
    nx.draw(
        topology,
        pos=positions,
        node_color=colors,
        node_size=sizes,
        labels=labels,
        font_size=6,
        font_weight="bold",
        font_color="whitesmoke",
        width=link_widths,
    )

    # Saving a topology image in the disk
    plt.savefig(f"{output_filename}.png", dpi=120)


# Defining a seed value to enable reproducibility
random.seed(1)

# Creating list of map coordinates
MAP_SIZE = 3
map_coordinates = hexagonal_grid(x_size=MAP_SIZE, y_size=MAP_SIZE)

# Creating regions to represent different locations in the map
region_labels = ["CT", "HK", "TK", "SE", "OS", "MU", "SI", "SY", "CA", "FR", "ST", "MI", "IR", "LO", "PA", "SP"]
for index, coordinates in enumerate(map_coordinates):
    # Creating the region object
    region = Region()
    region.label = region_labels[index]
    region.coordinates = coordinates


# Creating data centers owned by different providers
providers = [1, 2, 3]
data_centers_per_region = 2

allocation_cost_values = [
    {"Web Server": 100, "File Storage": 150, "Database": 200},
    {"Web Server": 200, "File Storage": 150, "Database": 100},
    {"Web Server": 150, "File Storage": 150, "Database": 150},
]
data_center_allocation_costs = uniform(n_items=Region.count() * data_centers_per_region, valid_values=allocation_cost_values)

data_center_capacity_values = [60, 120]
data_center_capacities = uniform(n_items=Region.count() * data_centers_per_region, valid_values=data_center_capacity_values)
data_center_provider_ids = uniform(n_items=Region.count() * data_centers_per_region, valid_values=providers)

for provider_id in providers:
    # Creating the provider object
    provider = Provider()

for region in Region.all():
    for _ in range(data_centers_per_region):
        # Creating the data center object
        data_center = DataCenter()

        # Connecting the data center to its region
        region.data_centers.append(data_center)
        data_center.region = region

        # Defining the data center attributes
        data_center.capacity = data_center_capacities[DataCenter.count() - 1]
        data_center.allocation_cost["Web Server"] = data_center_allocation_costs[DataCenter.count() - 1]["Web Server"]
        data_center.allocation_cost["File Storage"] = data_center_allocation_costs[DataCenter.count() - 1]["File Storage"]
        data_center.allocation_cost["Database"] = data_center_allocation_costs[DataCenter.count() - 1]["Database"]

        # Connecting the data center to its provider
        provider = Provider.find_by_id(data_center_provider_ids[DataCenter.count() - 1])
        data_center.provider = provider
        provider.data_centers.append(data_center)


# Creating a partially-connected mesh network topology
partially_connected_hexagonal_mesh(
    network_nodes=Region.all(),
    link_specifications=[
        {"number_of_objects": 16, "delay": 1},
    ],
)

link_delays = [
    {"regions": dict(["CT", "SE"]), "delay": round(387.92)},
    {"regions": dict(["CT", "HK"]), "delay": round(266.91)},
    {"regions": dict(["HK", "SE"]), "delay": round(38.64)},
    {"regions": dict(["HK", "OS"]), "delay": round(45.23)},
    {"regions": dict(["HK", "TK"]), "delay": round(53.17)},
    {"regions": dict(["TK", "OS"]), "delay": round(10.33)},
    {"regions": dict(["TK", "MU"]), "delay": round(129.8)},
    {"regions": dict(["SE", "SI"]), "delay": round(77.54)},
    {"regions": dict(["SE", "SY"]), "delay": round(146.44)},
    {"regions": dict(["SE", "OS"]), "delay": round(30.16)},
    {"regions": dict(["OS", "SY"]), "delay": round(118.54)},
    {"regions": dict(["OS", "CA"]), "delay": round(149.81)},
    {"regions": dict(["OS", "MU"]), "delay": round(122.17)},
    {"regions": dict(["MU", "CA"]), "delay": round(189.08)},
    {"regions": dict(["SI", "SY"]), "delay": round(93.92)},
    {"regions": dict(["SY", "CA"]), "delay": round(198.09)},
]
for link in Topology.first().edges(data=True):
    link_regions = dict([link[0].label, link[1].label])
    link_delay = next(link_metadata["delay"] for link_metadata in link_delays if link_metadata["regions"] == link_regions)
    link[2]["delay"] = link_delay
    print(f"{link}")


# Creating users and their composite applications
application_specifications = [
    {"number_of_objects": 12, "services": ["Web Server"]},
    {"number_of_objects": 12, "services": ["Web Server", "File Storage"]},
    {"number_of_objects": 12, "services": ["Web Server", "Database"]},
    {"number_of_objects": 12, "services": ["Web Server", "File Storage", "Database"]},
    {"number_of_objects": 12, "services": ["Web Server", "Database", "File Storage"]},
]

# Defining user delay SLA values
delay_slas = uniform(
    n_items=sum([app_spec["number_of_objects"] for app_spec in application_specifications]),
    valid_values=[100, 150, 200],
    shuffle_distribution=True,
)

# Defining service demands
number_of_services = sum([app_spec["number_of_objects"] * len(app_spec["services"]) for app_spec in application_specifications])
service_demand_values = [2, 4, 6, 8]
service_demands = uniform(
    n_items=number_of_services,
    valid_values=service_demand_values,
    shuffle_distribution=True,
)

for app_spec in random.sample(application_specifications, len(application_specifications)):
    for _ in range(app_spec["number_of_objects"]):
        application = Application()

        # Creating the user that access the application
        user = User()
        user.delay_sla = delay_slas[user.id - 1]
        user.region = random.choice(Region.all())
        user.region.users.append(user)

        # Defining the relationship attributes between the user and the application
        user.application = application
        application.user = user

        # Creating the services that compose the application
        for service_type in app_spec["services"]:

            # Creating the service object
            service = Service()
            service.label = service_type
            service.demand = service_demands[service.id - 1]

            # Connecting the application to its new service
            application.services.append(service)
            service.application = application


print("\n\n=== INFRASTRUCTURE ===")
for region in Region.all():
    cap = sum(dc.capacity for dc in region.data_centers)
    print(f"{region}. Overall Capacity: {cap}. Users: {region.users}")
    for dc in region.data_centers:
        print(f"\t{dc}. Provider: {dc.provider}. Capacity: {dc.capacity}. Allocation cost: {dc.allocation_cost}")

print("\n\n=== USERS ===")
for user in User.all():
    overall_demand = sum(service.demand for service in user.application.services)
    print(
        f"\t{user} ({user.region}). SLA: {user.delay_sla}. Demand: {overall_demand}. Services: {[s.label for s in user.application.services]}"
    )

print("\n\n=== USERS ===")
overall_capacity = sum(sum(data_center.capacity for data_center in region.data_centers) for region in Region.all())
overall_demand = sum(sum(service.demand for service in user.application.services) for user in User.all())

print(f"Regions: {Region.count()}")
print(f"Data Centers: {DataCenter.count()}")
print(f"Applications: {Application.count()}")
print(f"Services: {Service.count()}")
print(f"Overall Occupation: {round(overall_demand * 100 / overall_capacity, 2)}%")
print(f"Overall Capacity: {overall_capacity}")
print(f"Overall Demand: {overall_demand}")


# Exporting scenario
ComponentManager.export_scenario(save_to_file=True, file_name="dataset1")
