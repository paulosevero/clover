""" Contains topology-related functionality."""
# Component manager
from simulator.component_manager import ComponentManager

# Python libraries
import networkx as nx


class Topology(ComponentManager, nx.Graph):

    # Class attributes that allow this class to use helper methods from ComponentManager
    _instances = []
    _object_count = 0

    def __init__(self) -> object:
        # Adding the new object to the list of instances of its class
        self.__class__._instances.append(self)

        # Object's class instance ID
        self.__class__._object_count += 1
        self.id = self.__class__._object_count

        # Calling NetworkX's constructor
        nx.Graph.__init__(self)

    def calculate_path_delay(self, path: list) -> int:
        """Calculates the communication delay of a network path.
        Args:
            path (list): Network path whose delay will be calculated.
        Returns:
            path_delay (int): Network path delay.
        """
        path_delay = 0

        # Calculates the communication delay based on the delay property of each network link in the path
        path_delay = nx.classes.function.path_weight(G=self, path=path, weight="delay")

        return path_delay
