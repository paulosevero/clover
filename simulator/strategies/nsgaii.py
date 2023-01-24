# Importing simulator components
from simulator.components.data_center import DataCenter
from simulator.components.service import Service

# Importing helper methods
from simulator.helper_methods import *

# Importing Pymoo components
from pymoo.util.display import Display
from pymoo.core.problem import Problem
from pymoo.optimize import minimize
from pymoo.factory import get_crossover, get_mutation
from pymoo.algorithms.moo.nsga2 import NSGA2

# Importing Python libraries
import numpy as np
from random import sample

# Variable that defines the NSGA-II algorithm's verbosity
VERBOSE = True


def random_fit() -> list:
    """Custom algorithm that generates random placement solutions.
    Returns:
        placement (list): Generated placement solution.
    """
    services = sample(Service.all(), Service.count())

    for service in services:
        data_centers = sample(DataCenter.all(), DataCenter.count())

        for data_center in data_centers:
            # Checking if the data center would have resources to host the service
            if data_center.capacity >= service.demand:
                provision_service(user=service.application.user, service=service, data_center=data_center)
                break

    placement = [service.data_center.id for service in Service.all()]

    reset_scenario()

    return placement


class TheaDisplay(Display):
    """Creates a visualization on how the genetic algorithm is evolving throughout the generations."""

    def _do(self, problem: object, evaluator: object, algorithm: object):
        """Defines the way information about the genetic algorithm is printed after each generation.
        Args:
            problem (object): Instance of the problem being solved.
            evaluator (object): Object that makes modifications before calling the problem's evaluate function.
            algorithm (object): Algorithm being executed.
        """
        super()._do(problem, evaluator, algorithm)

        objective_1 = int(np.min(algorithm.pop.get("F")[:, 0]))
        objective_2 = int(np.min(algorithm.pop.get("F")[:, 1]))

        overloaded_data_centers = int(np.min(algorithm.pop.get("CV")[:, 0]))

        self.output.append("SLAV", objective_1)
        self.output.append("Cost", objective_2)
        self.output.append("Overloaded SVs", overloaded_data_centers)


class PlacementProblem(Problem):
    """Describes the application placement as an optimization problem."""

    def __init__(self, **kwargs):
        """Initializes the problem instance."""
        super().__init__(n_var=Service.count(), n_obj=2, n_constr=1, xl=1, xu=DataCenter.count(), type_var=int, **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        """Evaluates solutions according to the problem objectives.
        Args:
            x (list): Solution or set of solutions that solve the problem.
            out (dict): Output of the evaluation function.
        """
        output = [self.get_fitness_score_and_constraints(solution=solution) for solution in x]

        out["F"] = np.array([item[0] for item in output])
        out["G"] = np.array([item[1] for item in output])

    def get_fitness_score_and_constraints(self, solution: list) -> tuple:
        """Calculates the fitness score and penalties of a solution based on the problem definition.
        Args:
            solution (list): Placement scheme.
        Returns:
            output (tuple): Output of the evaluation function containing the fitness scores of the solution and its penalties.
        """
        # Applying the placement scheme suggested by the chromosome
        apply_placement(solution=solution)

        # Calculating objectives and penalties
        output = evaluate_placement()

        # Resetting the placement scheme suggested by the chromosome
        reset_scenario()

        return output


def nsgaii(parameters: dict = {}):
    print(parameters)
    # Parsing the NSGA-II parameters
    pop_size = parameters["pop_size"]
    n_gen = parameters["n_gen"]
    cross_prob = parameters["cross_prob"]
    mut_prob = parameters["mut_prob"]

    # Generating initial population for the NSGA-II algorithm
    initial_population = []
    while len(initial_population) < pop_size:
        placement = random_fit()
        if placement not in initial_population:
            initial_population.append(placement)

    # Defining the NSGA-II attributes
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=np.array(initial_population),
        crossover=get_crossover("int_ux", prob=cross_prob),
        mutation=get_mutation("int_pm", prob=mut_prob),
        eliminate_duplicates=True,
    )

    # Running the NSGA-II algorithm
    problem = PlacementProblem()
    res = minimize(problem, algorithm, termination=("n_gen", n_gen), seed=1, verbose=VERBOSE, display=TheaDisplay())

    # Parsing the NSGA-II's output
    solutions = []
    for i in range(len(res.X)):
        solution = {
            "Placement": res.X[i].tolist(),
            "SLAV": res.F[i][0],
            "COST": res.F[i][1],
            "Overloaded DCs": res.CV[i][0].tolist(),
        }
        solutions.append(solution)

    # Applying the a placement scheme found by the NSGA-II algorithm
    min_and_max = find_minimum_and_maximum(metadata=solutions)

    best_solution = sorted(
        solutions, key=lambda solution: (solution["Overloaded DCs"], min_and_max["minimum"]["SLAV"] + min_and_max["minimum"]["COST"])
    )[0]["Placement"]

    apply_placement(solution=best_solution)
