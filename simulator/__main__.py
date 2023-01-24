# Importing simulation components
from simulator.simulator import Simulator
from simulator.components import *
from simulator.helper_methods import *

# Importing placement strategies
from simulator.strategies import *

# Importing Python libraries
from random import seed
import argparse
import time
import csv


def main(seed_value: int, algorithm: str, dataset: str, parameters: dict = {}):
    # Setting a seed value to enable reproducibility
    seed(seed_value)

    # Creating a Simulator object
    simulator = Simulator(
        placement_algorithm=eval(algorithm),
        placement_algorithm_parameters=parameters,
    )

    # Loading the dataset
    simulator.initialize(input_file=dataset)

    print(f"Data Centers: {DataCenter.count()}")
    print(f"Service: {Service.count()}")
    print(f"=== PROVIDERS ===")
    for provider in Provider.all():
        print(f"{provider}. Data Centers: {len(provider.data_centers)}")
    print(f"=== REGIONS ===")
    for region in Region.all():
        print(f"{region}. Data Centers: {len(region.data_centers)}")
    exit(1)

    # Executing the simulation
    simulator.run()

    metrics = calculate_metrics()
    print("\n\n==== SIMULATION OUTPUT ====")
    print(f"Algorithm: {algorithm}")
    for metric_name, metric_value in metrics.items():
        print(f"{metric_name}: {metric_value}")
    print("")

    simulation_output = {"algorithm": algorithm, **parameters, **metrics}

    # Exporting the simulation results to a CSV file
    # Parsing the algorithm's parameters string
    output_file_name = f"{str(time.time()).replace('.', '-')}-{algorithm};"
    for key, value in parameters.items():
        output_file_name += f"{key}={value};"

    if algorithm == "nsgaii":
        with open(f"logs/{output_file_name}.csv", "w") as file:
            writer = csv.DictWriter(file, simulation_output.keys())
            writer.writeheader()
            writer.writerow(simulation_output)

    # Resetting the simulation scenario
    reset_scenario()


if __name__ == "__main__":
    # Parsing named arguments from the command line
    parser = argparse.ArgumentParser()

    # Generic arguments
    parser.add_argument("--seed", "-s", help="Seed value for EdgeSimPy", default="1")
    parser.add_argument("--dataset", "-d", help="Dataset file")
    parser.add_argument("--algorithm", "-a", help="Algorithm that will be executed")

    # NSGA-II arguments
    parser.add_argument("--pop_size", "-p", help="Population size", default="0")
    parser.add_argument("--n_gen", "-g", help="Number of generations", default="0")
    parser.add_argument("--cross_prob", "-c", help="Crossover probability (0.0 to 1.0)", default="1")
    parser.add_argument("--mut_prob", "-m", help="Mutation probability (0.0 to 1.0)", default="0")

    args = parser.parse_args()

    parameters = {
        "pop_size": int(args.pop_size),
        "n_gen": int(args.n_gen),
        "cross_prob": float(args.cross_prob),
        "mut_prob": float(args.mut_prob),
    }

    main(seed_value=int(args.seed), algorithm=args.algorithm, dataset=args.dataset, parameters=parameters)
