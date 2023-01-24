""" Contains all the simulation management functionality."""
# Component manager
from simulator.component_manager import ComponentManager

# Simulation components
from simulator.components import *

# Python libraries
import os
import json
from urllib.parse import urlparse
from urllib.request import urlopen
from typing import Callable


class Simulator(ComponentManager):
    """Class responsible for managing the simulation."""

    # Class attributes that allow this class to use helper methods from ComponentManager
    _instances = []
    _object_count = 0

    def __init__(self, placement_algorithm: Callable = None, placement_algorithm_parameters: dict = {}) -> object:
        """Creates a Simulator object.
        Args:
            placement_algorithm (Callable, optional): Placement management algorithm executed in the simulation. Defaults to None.
            placement_algorithm_parameters (dict, optional): Parameters read by the placement algorithm. Defaults to {}.
        Returns:
            object: Created Simulator object.
        """
        # Resource management algorithm
        self.placement_algorithm = placement_algorithm
        self.placement_algorithm_parameters = placement_algorithm_parameters

        # Attribute that stores the network topology used during the simulation
        self.topology = None

        # Storing a reference to the Simulator object inside the ComponentManager class
        ComponentManager._ComponentManager__model = self

        # Adding the new object to the list of instances of its class
        self.__class__._instances.append(self)

    def initialize(self, input_file: str) -> None:
        # Resetting the list of instances of component classes
        for component_class in ComponentManager.__subclasses__():
            if component_class.__name__ != "Simulator":
                component_class._object_count = 0
                component_class._instances = []

        # Declaring an empty variable that will receive the dataset metadata (if user passes valid information)
        data = None

        # If "input_file" represents a valid URL, parses its response
        if all([urlparse(input_file).scheme, urlparse(input_file).netloc]):
            data = json.loads(urlopen(input_file).read())

        # If "input_file" points to the local filesystem, checks if the file exists and parses it
        if os.path.exists(input_file):
            with open(input_file, "r", encoding="UTF-8") as read_file:
                data = json.load(read_file)

        elif os.path.exists(f"{os.getcwd()}/{input_file}"):
            with open(f"{os.getcwd()}/{input_file}", "r", encoding="UTF-8") as read_file:
                data = json.load(read_file)

        # Raising exception if the dataset could not be loaded based on the specified arguments
        if type(data) is not dict:
            raise TypeError("The simulator could not load the dataset based on the specified arguments.")

        # Creating simulator components based on the specified input data
        missing_keys = [key for key in data.keys() if key not in globals()]
        if len(missing_keys) > 0:
            raise Exception(f"\n\nCould not find component classes named: {missing_keys}. Please check your input file.\n\n")

        # Creating a list that will store all the relationships among components
        components = []

        # Creating the topology object and storing a reference to it as an attribute of the Simulator instance
        self.topology = Topology()

        # Creating simulator components
        for key in data.keys():
            if key != "Simulator" and key != "Topology":
                for object_metadata in data[key]:
                    new_component = globals()[key]._from_dict(dictionary=object_metadata["attributes"])
                    new_component.relationships = object_metadata["relationships"]

                    if hasattr(new_component, "model") and hasattr(new_component, "unique_id"):
                        self.initialize_agent(agent=new_component)

                    components.append(new_component)

        # Defining relationships between components
        for component in components:
            for key, value in component.relationships.items():
                # Defining attributes referencing callables (i.e., functions and methods)
                if type(value) == str and value in globals():
                    setattr(component, f"{key}", globals()[value])

                # Defining attributes referencing lists of components (e.g., lists of edge servers, users, etc.)
                elif type(value) == list:
                    attribute_values = []
                    for item in value:
                        obj = (
                            globals()[item["class"]].find_by_id(item["id"])
                            if type(item) == dict and "class" in item and item["class"] in globals()
                            else None
                        )

                        if obj == None:
                            raise Exception(f"List relationship '{key}' of component {component} has an invalid item: {item}.")

                        attribute_values.append(obj)

                    setattr(component, f"{key}", attribute_values)

                # Defining attributes that reference a single component (e.g., an edge server, an user, etc.)
                elif type(value) == dict and "class" in value and "id" in value:
                    obj = (
                        globals()[value["class"]].find_by_id(value["id"])
                        if type(value) == dict and "class" in value and value["class"] in globals()
                        else None
                    )

                    if obj == None:
                        raise Exception(f"Relationship '{key}' of component {component} references an invalid object: {value}.")

                    setattr(component, f"{key}", obj)

                # Defining attributes that reference a a dictionary of components (e.g., {"1": {"class": "A", "id": 1}} )
                elif type(value) == dict and all(
                    type(entry) == dict and "class" in entry and "id" in entry for entry in value.values()
                ):
                    attribute = {}
                    for k, v in value.items():
                        obj = globals()[v["class"]].find_by_id(v["id"]) if "class" in v and v["class"] in globals() else None
                        if obj == None:
                            raise Exception(f"Relationship '{key}' of component {component} references an invalid object: {value}.")
                        attribute[k] = obj

                    setattr(component, f"{key}", attribute)

                # Defining "None" attributes
                elif value == None:
                    setattr(component, f"{key}", None)

                else:
                    raise Exception(f"Couldn't add the relationship {key} with value {value}. Please check your dataset.")

        # Filling the network topology
        for link in NetworkLink.all():
            # Adding the nodes connected by the link to the topology
            self.topology.add_node(link.nodes[0])
            self.topology.add_node(link.nodes[1])

            # Replacing NetworkX's default link dictionary with the NetworkLink object
            self.topology.add_edge(link.nodes[0], link.nodes[1])
            self.topology._adj[link.nodes[0]][link.nodes[1]] = link
            self.topology._adj[link.nodes[1]][link.nodes[0]] = link

    def run(self) -> None:
        self.placement_algorithm(parameters=self.placement_algorithm_parameters)
