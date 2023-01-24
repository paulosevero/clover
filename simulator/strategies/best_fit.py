# Simulation components
from simulator.components.data_center import DataCenter
from simulator.components.application import Application

# Helper methods
from simulator.helper_methods import *


def best_fit(parameters={}):
    """Provisions services on the data centers with the least amount of free resources that could accommodate them."""
    for application in Application.all():
        for service in application.services:
            data_centers = sorted(DataCenter.all(), key=lambda data_center: data_center.capacity - data_center.demand)

            for data_center in data_centers:
                # Checking if the data center would have resources to host the service
                if data_center.demand + service.demand <= data_center.capacity:
                    provision_service(data_center=data_center, service=service, user=service.application.user)
                    break
