""" Contains network-link-related functionality."""
# Simulation components
from simulator.component_manager import ComponentManager


class NetworkLink(dict, ComponentManager):
    """Class that represents a network link."""

    # Class attributes that allow this class to use helper methods from ComponentManager
    _instances = []
    _object_count = 0

    def __init__(self, obj_id: int = None) -> object:
        """Creates a NetworkLink object.
        Args:
            obj_id (int, optional): Object identifier.
        Returns:
            object: Created NetworkLink object.
        """
        # Adding the new object to the list of instances of its class
        self.__class__._instances.append(self)

        # Object's class instance ID
        self.__class__._object_count += 1
        if obj_id is None:
            obj_id = self.__class__._object_count
        self["id"] = obj_id

        # Reference to the network topology
        self["topology"] = None

        # List of network nodes that are connected by the link
        self["nodes"] = []

        # Link delay
        self["delay"] = 0

    def __getattr__(self, attribute_name: str):
        """Retrieves an object attribute by its name.
        Args:
            attribute_name (str): Name of the attribute to be retrieved.
        Returns:
            (any): Attribute value.
        """
        if attribute_name in self:
            return self[attribute_name]
        else:
            raise AttributeError(f"Object {self} has no such attribute '{attribute_name}'.")

    def __setattr__(self, attribute_name: str, attribute_value: object):
        """Overrides the value of an object attribute.
        Args:
            attribute_name (str): Name of the attribute to be changed.
            attribute_value (object): Value for the attribute.
        """
        self[attribute_name] = attribute_value

    def __delattr__(self, attribute_name: str):
        """Deletes an object attribute by its name.
        Args:
            attribute_name (str): Name of the attribute to be deleted.
        """
        if attribute_name in self:
            del self[attribute_name]
        else:
            raise AttributeError(f"Object {self} has no such attribute '{attribute_name}'.")

    def _to_dict(self) -> dict:
        """Method that overrides the way the object is formatted to JSON."
        Returns:
            dict: JSON-friendly representation of the object as a dictionary.
        """
        dictionary = {
            "attributes": {
                "id": self.id,
                "delay": self.delay,
            },
            "relationships": {
                "topology": {"class": "Topology", "id": self.topology.id},
                "nodes": [{"class": type(node).__name__, "id": node.id} for node in self.nodes],
            },
        }
        return dictionary
