# Importing simulator components
from simulator.components.application import Application

# Importing helper methods
from simulator.helper_methods import *


def proposed_algorithm(parameters: dict = {}):
    """Heuristic that performs a latency-aware cost-efficient provisioning of composite applications in multi-provider clouds.

    Args:
        parameters (dict, optional): Algorithm parameters. Defaults to {}.
    """
    # Calculating the delay and allocation cost scores of applications and sorting them accordingly
    applications_metadata = sorted(
        get_application_scores(), key=lambda app: app["norm_delay_score"] + app["norm_allocation_cost_score"], reverse=True
    )

    # Iterating over the sorted list of applications to provision their services
    for application_metadata in applications_metadata:
        application = application_metadata["object"]
        for service in application.services:
            data_centers_metadata = get_candidate_data_centers(service=service)

            data_centers = sorted(
                data_centers_metadata,
                key=lambda data_center: (data_center["respects_delay_sla"] + data_center["norm_allocation_cost_score"]),
                reverse=True,
            )

            for data_center_metadata in data_centers:
                data_center = data_center_metadata["object"]
                if data_center.capacity >= data_center.demand + service.demand:
                    provision_service(
                        service=service,
                        user=service.application.user,
                        data_center=data_center,
                    )
                    break


def get_application_scores() -> float:
    """Calculates the applications' scores used to define the order in which applications will be provisioned.

    Returns:
        applications (float): Applications' metadata (application objects and their scores).
    """
    applications = []

    for application in Application.all():
        # Gathering the list of data centers with enough resources to host the application services
        # that are close enough to the application's user that could be used to host the application
        # services without violating the delay SLA
        free_resources_that_dont_violate_sla = 0

        for data_center in DataCenter.all():
            data_center_delay = calculate_path_delay(origin_region=application.user.region, target_region=data_center.region)
            if data_center_delay <= application.user.delay_sla:
                free_resources_that_dont_violate_sla += data_center.capacity - data_center.demand

        delay_score = 1 / free_resources_that_dont_violate_sla

        # Finding the minimum and maximum allocation costs for each type of service that composes the application
        allocation_cost_score = 0
        for service in application.services:
            allocation_costs = [data_center.allocation_cost[service.label] for data_center in DataCenter.all()]
            min_cost = min(allocation_costs)
            max_cost = max(allocation_costs)

            potential_cost_reduction = max(1, max_cost - min_cost)
            items_max_profit = 1 / (sum(1 for cost in allocation_costs if cost == min_cost) * min_cost)

            allocation_cost_score += potential_cost_reduction * items_max_profit

        application_metadata = {
            "object": application,
            "delay_score": delay_score,
            "allocation_cost_score": allocation_cost_score,
        }

        applications.append(application_metadata)

    # Calculating the normalized application scores
    min_max_scores = find_minimum_and_maximum(applications)
    for application_metadata in applications:
        norm_delay_score = get_norm(
            metadata=application_metadata,
            attr_name="delay_score",
            min=min_max_scores["minimum"],
            max=min_max_scores["maximum"],
        )
        norm_allocation_cost_score = get_norm(
            metadata=application_metadata,
            attr_name="allocation_cost_score",
            min=min_max_scores["minimum"],
            max=min_max_scores["maximum"],
        )

        application_metadata["norm_delay_score"] = norm_delay_score
        application_metadata["norm_allocation_cost_score"] = norm_allocation_cost_score

    return applications


def get_candidate_data_centers(service: object):
    """Function that calculates delay SLA and allocation cost scores for the data centers that could host a given service.

    Args:
        service (object): Service to be provisioned.
    """
    # Gathering information about the previous item in the application's communication chain
    communication_chain = list([service.application.user] + service.application.services)
    previous_item_in_chain = communication_chain[communication_chain.index(service) - 1]
    previous_region = (
        previous_item_in_chain.region if type(previous_item_in_chain) == User else previous_item_in_chain.data_center.region
    )

    # Declaring a list that will host the data centers metadata
    data_centers = []

    for data_center in DataCenter.all():
        # Checking if the data center would violate the application's user delay SLA
        delay = calculate_path_delay(origin_region=previous_region, target_region=data_center.region)
        respects_delay_sla = 1 if delay <= service.application.user.delay_sla else 0

        # Calculating the data center's allocation cost score
        allocation_cost_score = 1 / data_center.allocation_cost[service.label]

        data_center_metadata = {
            "object": data_center,
            "delay": delay,
            "respects_delay_sla": respects_delay_sla,
            "allocation_cost_score": allocation_cost_score,
        }

        data_centers.append(data_center_metadata)

    # Calculating the normalized data centers' allocation cost scores
    min_max_scores = find_minimum_and_maximum(data_centers)
    for data_center_metadata in data_centers:
        norm_allocation_cost_score = get_norm(
            metadata=data_center_metadata,
            attr_name="allocation_cost_score",
            min=min_max_scores["minimum"],
            max=min_max_scores["maximum"],
        )

        data_center_metadata["norm_allocation_cost_score"] = norm_allocation_cost_score

    return data_centers
