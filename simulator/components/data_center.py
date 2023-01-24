""" Contains data-center-related functionality."""
# Simulation components
from simulator.component_manager import ComponentManager


class DataCenter(ComponentManager):

    # Class attributes that allow this class to use helper methods from the ComponentManager
    _instances = []
    _object_count = 0

    def __init__(self, obj_id: int = None) -> object:
        """Creates a DataCenter object.

        Args:
            obj_id (int, optional): Object identifier. Defaults to None.

        Returns:
            object: Created DataCenter object.
        """
        # Adding the new object to the list of instances of its class
        self.__class__._instances.append(self)

        # Object's class instance ID
        self.__class__._object_count += 1
        if obj_id is None:
            obj_id = self.__class__._object_count
        self.id = obj_id

        # Data center's alias
        self.alias = ""

        # Data center's capacity and demand
        self.capacity = 0
        self.demand = 0

        # References to the services hosted on the data center
        self.services = []

        # Data center's allocation cost
        self.allocation_cost = {}

        # Reference to the region where the data center is located
        self.region = None

        # Reference to the provider that owns the data center
        self.provider = None

    def _to_dict(self) -> dict:
        """Method that overrides the way the object is formatted to JSON."
        Returns:
            dict: JSON-friendly representation of the object as a dictionary.
        """
        dictionary = {
            "attributes": {
                "id": self.id,
                "alias": self.alias,
                "capacity": self.capacity,
                "demand": self.demand,
                "allocation_cost": self.allocation_cost,
            },
            "relationships": {
                "region": {"class": type(self.region).__name__, "id": self.region.id},
                "provider": {"class": type(self.provider).__name__, "id": self.provider.id},
                "services": [{"class": type(service).__name__, "id": service.id} for service in self.services],
            },
        }
        return dictionary
