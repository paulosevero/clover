""" Contains user-related functionality."""
# Simulation components
from simulator.component_manager import ComponentManager
from simulator.components.topology import Topology
from simulator.components.region import Region

# Python libraries
import networkx as nx


class User(ComponentManager):

    # Class attributes that allow this class to use helper methods from the ComponentManager
    _instances = []
    _object_count = 0

    def __init__(self, obj_id: int = None) -> object:
        """Creates a User object.

        Args:
            obj_id (int, optional): Object identifier. Defaults to None.

        Returns:
            object: Created User object.
        """
        # Adding the new object to the list of instances of its class
        self.__class__._instances.append(self)

        # Object's class instance ID
        self.__class__._object_count += 1
        if obj_id is None:
            obj_id = self.__class__._object_count
        self.id = obj_id

        # User's delay and delay SLA
        self.delay_sla = 0
        self.delay = float("inf")

        # User's communication path (list of links used to communicate the user to the services that compose his application)
        self.communication_path = []

        # User's coordinates
        self.coordinates = 0

        # Reference to the user's region
        self.region = None

        # Reference to the application accessed by the user
        self.application = None

    def _to_dict(self) -> dict:
        """Method that overrides the way the object is formatted to JSON."
        Returns:
            dict: JSON-friendly representation of the object as a dictionary.
        """
        dictionary = {
            "attributes": {
                "id": self.id,
                "delay_sla": self.delay_sla,
                "coordinates": self.coordinates,
                "communication_path": self.communication_path,
            },
            "relationships": {
                "region": {"class": type(self.region).__name__, "id": self.region.id} if self.region else None,
                "application": {"class": type(self.application).__name__, "id": self.application.id} if self.application else None,
            },
        }
        return dictionary

    def _compute_delay(self) -> int:
        """Computes the delay of an application accessed by the user.

        Returns:
            delay (int): User-perceived delay.
        """
        topology = Topology.first()

        # Resetting the user delay
        self.delay = 0

        # Adding the communication path delay to the application's delay
        for path in self.communication_path:
            self.delay += topology.calculate_path_delay(path=[Region.find_by_id(i) for i in path])

        return self.delay

    def set_communication_path(self, communication_path: list = []) -> list:
        """Updates the set of links used during the communication of user and its application.

        Args:
            communication_path (list, optional): User-specified communication path. Defaults to [].

        Returns:
            list: Updated communication path.
        """
        topology = Topology.first()

        # Defining communication path
        if len(communication_path) > 0:
            self.communication_path = communication_path
        else:
            self.communication_path = []

            service_hosts_regions = [service.data_center.region for service in self.application.services if service.data_center]
            communication_chain = [self.region] + service_hosts_regions

            # Defining a set of links to connect the items in the application's service chain
            for i in range(len(communication_chain) - 1):

                # Defining origin and target nodes
                origin = communication_chain[i]
                target = communication_chain[i + 1]

                # Finding and storing the best communication path between the origin and target nodes
                if origin == target:
                    path = []
                else:
                    path = nx.shortest_path(
                        G=topology,
                        source=origin,
                        target=target,
                        weight="delay",
                        method="dijkstra",
                    )

                # Adding the best path found to the communication path
                self.communication_path.append([region.id for region in path])

        # Computing application's delay
        self._compute_delay()

        return self.communication_path
