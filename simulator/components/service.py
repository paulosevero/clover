""" Contains application-related functionality."""
# Simulation components
from simulator.component_manager import ComponentManager


class Service(ComponentManager):

    # Class attributes that allow this class to use helper methods from the ComponentManager
    _instances = []
    _object_count = 0

    def __init__(self, obj_id: int = None) -> object:
        """Creates a Service object.

        Args:
            obj_id (int, optional): Object identifier. Defaults to None.

        Returns:
            object: Created Service object.
        """
        # Adding the new object to the list of instances of its class
        self.__class__._instances.append(self)

        # Object's class instance ID
        self.__class__._object_count += 1
        if obj_id is None:
            obj_id = self.__class__._object_count
        self.id = obj_id

        # Service demand
        self.demand = 0

        # Service label
        self.label = ""

        # Reference to the data center that hosts the service
        self.data_center = None

        # Reference to the application to which the service belongs to
        self.application = None

    def _to_dict(self) -> dict:
        """Method that overrides the way the object is formatted to JSON."
        Returns:
            dict: JSON-friendly representation of the object as a dictionary.
        """
        dictionary = {
            "attributes": {
                "id": self.id,
                "demand": self.demand,
                "label": self.label,
            },
            "relationships": {
                "data_center": {"class": type(self.data_center).__name__, "id": self.data_center.id} if self.data_center else None,
                "application": {"class": type(self.application).__name__, "id": self.application.id},
            },
        }
        return dictionary
