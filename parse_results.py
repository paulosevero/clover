# Python libraries
import os
import csv


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


# Gathering the list of dataset files inside the "logs" directory
dataset_files = os.listdir(path=f"{os.getcwd()}/logs")

# Declaring list variable that will hold the simulation results
results = []

for dataset_file in dataset_files:
    if ".csv" in dataset_file:
        print(f"=== {dataset_file} ===")

        with open(f"{os.getcwd()}/logs/{dataset_file}") as f:
            reader = csv.DictReader(f)

            for row in reader:
                results.append(row)

# Finding minimum and maximum values
minimum = {
    "sla_violations": float("inf"),
    "overall_allocation_cost": float("inf"),
}
maximum = {
    "sla_violations": float("-inf"),
    "overall_allocation_cost": float("-inf"),
}
for result in results:
    for metric in minimum.keys():
        result[metric] = float(result[metric])
        if minimum[metric] > result[metric]:
            minimum[metric] = result[metric]
        if maximum[metric] < result[metric]:
            maximum[metric] = result[metric]

# Calculating normalized values of chosen metrics
for result in results:
    for metric in minimum.keys():
        result[f"norm_{metric}"] = min_max_norm(x=result[metric], min=minimum[metric], max=maximum[metric])


# Exporting parsed results to a CSV file
with open("results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
