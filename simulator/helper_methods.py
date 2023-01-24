"""Contains a set of methods that support the simulation"""
# Simulator components
from simulator.components.topology import Topology
from simulator.components.data_center import DataCenter
from simulator.components.user import User
from simulator.components.service import Service

# Python libraries
import networkx as nx


def provision_service(user: object, service: object, data_center: object):
    """Provisions a service on a data center.

    Args:
        user (object): User that accesses the application.
        service (object): Service to be provisioned.
        data_center (object): Data center that will host the service.
    """
    # Updating the data center's resource usage
    data_center.demand += service.demand

    # Creating relationship between the host and the registry
    service.data_center = data_center
    data_center.services.append(service)

    user.set_communication_path()


def apply_placement(solution: list):
    """Applies a placement scheme.

    Args:
        solution (list): Placement scheme.
    """
    for service_id, data_center_id in enumerate(solution, 1):
        service = Service.find_by_id(service_id)
        data_center = DataCenter.find_by_id(data_center_id)

        provision_service(user=service.application.user, service=service, data_center=data_center)


def reset_scenario():
    """Resets the simulation scenario."""
    # Resetting the data centers and services states
    for data_center in DataCenter.all():
        for service in data_center.services:
            service.data_center = None
        data_center.services = []
        data_center.demand = 0

    # Resetting the users states
    for user in User.all():
        user.delay = float("inf")
        user.communication_path = []


def find_shortest_path(origin_region: object, target_region: object) -> int:
    """Finds the shortest path (delay used as weight) between two regions (origin and target).
    Args:
        origin_region (object): Origin region.
        target_region (object): Target region.
    Returns:
        path (list): Shortest path between the origin and target regions.
    """
    topology = Topology.first()
    path = []

    if not hasattr(topology, "delay_shortest_paths"):
        topology.delay_shortest_paths = {}

    key = (origin_region, target_region)

    if key in topology.delay_shortest_paths.keys():
        path = topology.delay_shortest_paths[key]
    else:
        path = nx.shortest_path(G=topology, source=origin_region, target=target_region, weight="delay")
        topology.delay_shortest_paths[key] = path

    return path


def calculate_path_delay(origin_region: object, target_region: object) -> int:
    """Gets the distance (in terms of delay) between two regions (origin and target).
    Args:
        origin_region (object): Origin region.
        target_region (object): Target region.
    Returns:
        delay (int): Delay between the origin and target regions.
    """
    topology = Topology.first()

    path = find_shortest_path(origin_region=origin_region, target_region=target_region)
    delay = topology.calculate_path_delay(path=path)

    return delay


def calculate_metrics():
    # Declaring the variables that will accommodate the placement metrics
    sla_violations = 0
    overall_allocation_cost = 0
    overloaded_data_centers = 0

    # Calculating the number of SLA violations
    for user in User.all():
        user._compute_delay()
        if user.delay > user.delay_sla:
            sla_violations += 1

    # Calculating the allocation cost
    for data_center in DataCenter.all():
        for service in data_center.services:
            overall_allocation_cost += data_center.allocation_cost[service.label] * service.demand

    # Calculating the number of overloaded data centers
    for data_center in DataCenter.all():
        if data_center.demand > data_center.capacity:
            overloaded_data_centers += 1

    metrics = {
        "sla_violations": sla_violations,
        "overall_allocation_cost": overall_allocation_cost,
        "overloaded_data_centers": overloaded_data_centers,
    }

    return metrics


def evaluate_placement():
    """Evaluates a placement scheme based on the normalized number of SLA violations (delay) and allocation cost."""
    # Gathering placement metrics
    metrics = calculate_metrics()

    # Gathering a normalized number of SLA violations
    sla_violations = metrics["sla_violations"] / User.count() * 100

    # Gathering a normalized allocation cost
    max_allocation_cost_possible = sum([max(dc.allocation_cost.values()) * dc.capacity for dc in DataCenter.all()])
    overall_allocation_cost = metrics["overall_allocation_cost"] / max_allocation_cost_possible * 100

    # Gathering the number of overloaded data centers
    overloaded_data_centers = metrics["overloaded_data_centers"]

    # Aggregating results (problem objectives and constraints)
    objectives = (sla_violations, overall_allocation_cost)
    penalties = overloaded_data_centers
    output = (objectives, penalties)

    return output


def min_max_norm(x, min, max):
    """Normalizes a given value (x) using the Min-Max Normalization method.

    Args:
        x (any): Value that must be normalized.
        min (any): Minimum value known.
        max (any): Maximum value known.

    Returns:
        (any): Normalized value.
    """
    if min == max:
        return 1
    return (x - min) / (max - min)


def get_norm(metadata: dict, attr_name: str, min: dict, max: dict) -> float:
    """Wrapper to normalize a value using the Min-Max Normalization method.

    Args:
        metadata (dict): Dictionary that contains the metadata of the object whose values are being normalized.
        attr_name (str): Name of the attribute that must be normalized.
        min (dict): Dictionary that contains the minimum values of the attributes.
        max (dict): Dictionary that contains the maximum values of the attributes.
    Returns:
        normalized_value (float): Normalized value.
    """
    normalized_value = min_max_norm(x=metadata[attr_name], min=min[attr_name], max=max[attr_name])
    return normalized_value


def find_minimum_and_maximum(metadata: list):
    """Finds the minimum and maximum values of a list of dictionaries.

    Args:
        metadata (list): List of dictionaries that contains the analyzed metadata.

    Returns:
        min_and_max (dict): Dictionary that contains the minimum and maximum values of the attributes.
    """
    min_and_max = {
        "minimum": {},
        "maximum": {},
    }

    for metadata_item in metadata:
        for attr_name, attr_value in metadata_item.items():
            if attr_name != "object":
                # Updating the attribute's minimum value
                if (
                    attr_name not in min_and_max["minimum"]
                    or attr_name in min_and_max["minimum"]
                    and attr_value < min_and_max["minimum"][attr_name]
                ):
                    min_and_max["minimum"][attr_name] = attr_value

                # Updating the attribute's maximum value
                if (
                    attr_name not in min_and_max["maximum"]
                    or attr_name in min_and_max["maximum"]
                    and attr_value > min_and_max["maximum"][attr_name]
                ):
                    min_and_max["maximum"][attr_name] = attr_value

    return min_and_max
