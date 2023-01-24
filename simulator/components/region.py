""" Contains region-related functionality."""
# Simulation components
from simulator.component_manager import ComponentManager


class Region(ComponentManager):

    # Class attributes that allow this class to use helper methods from the ComponentManager
    _instances = []
    _object_count = 0

    def __init__(self, obj_id: int = None) -> object:
        """Creates a Region object.

        Args:
            obj_id (int, optional): Object identifier. Defaults to None.

        Returns:
            object: Created Region object.
        """
        # Adding the new object to the list of instances of its class
        self.__class__._instances.append(self)

        # Object's class instance ID
        self.__class__._object_count += 1
        if obj_id is None:
            obj_id = self.__class__._object_count
        self.id = obj_id

        # Region's label
        self.label = ""

        # Region's coordinates
        self.coordinates = None

        # List of users connected to the region's network
        self.users = []

        # List of data centers within the region
        self.data_centers = []

    def _to_dict(self) -> dict:
        """Method that overrides the way the object is formatted to JSON."
        Returns:
            dict: JSON-friendly representation of the object as a dictionary.
        """
        dictionary = {
            "attributes": {
                "id": self.id,
                "coordinates": self.coordinates,
            },
            "relationships": {
                "data_centers": [{"class": type(data_center).__name__, "id": data_center.id} for data_center in self.data_centers],
                "users": [{"class": type(user).__name__, "id": user.id} for user in self.users],
            },
        }
        return dictionary
