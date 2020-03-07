import gevent
import json
import random
import os
import time
from locust import events, HttpLocust, TaskSet, task

from personas import common


class PersonaTaskSet(TaskSet):
    def on_start(self):
        self.client.verify = False
        self.max_profiles = int(os.environ["VRP_MAX_PROFILES"]) if "VRP_MAX_PROFILES" in os.environ else 1
        self.max_locations = int(os.environ["VRP_MAX_LOCATIONS"]) if "VRP_MAX_LOCATIONS" in os.environ else 10
        self.api_key = common.get_api_key()
        common.setup_locust_debugging()

    @task
    def get_vrp(self):

        base_url = common.get_base_url("vrp", subpath_required=False)

        # set a payload of random locations
        vehicles, vehicle_types = get_random_vehicles_and_types(self.max_profiles)
        data = {
            "vehicles": vehicles,
            "vehicle_types": vehicle_types,
            "services": get_random_services(self.max_locations),
        }
        payload = json.dumps(data)

        # optimize
        url = f"{base_url}/optimize?key={self.api_key}"
        headers = {"content-type": "application/json"}
        with self.client.post(url, catch_response=True, data=payload, headers=headers, name="VRP complex Optimize", timeout=60) as response:
            try:
                response_data = response.json()
            except json.decoder.JSONDecodeError as e:
                response.failure("VRP optimize failed, json decode error: {}\nCode: {}, Response text: {}".format(e, response.status_code, response.text))
                return
            if "job_id" not in response_data:
                response.failure(f"VRP optimize failed, no `job_id` in response. Response: {response_data}")
                return

            job_id = response.json()["job_id"]

        while True:
            url = f"{base_url}/solution/{job_id}?key={self.api_key}"
            with self.client.get(url, catch_response=True, name="VRP complex Solution", timeout=60) as response:
                try:
                    response_data = response.json()
                except json.decoder.JSONDecodeError as e:
                    response.failure("VRP solution failed, json decode error: {}\nCode: {}, Response text: {}".format(e, response.status_code, response.text))
                    return
                if response.status_code == 400:
                    response.failure("VRP solution failed, HTTP 400. {}".format(response.text))
                    return
                if "status" not in response_data:
                    response.failure("VRP solution failed, no `status` in response.")
                    return
                if response.json()["status"] == "finished":
                    break
                time.sleep(0.33) # maximum 3 GET requests per second


class PersonaVRP(HttpLocust):
    task_set = PersonaTaskSet
    weight = 10


def get_random_vehicles_and_types(max_profiles):
    vehicles = []
    vehicle_types = []
    vrp_tomtom_probability = float(os.environ["VRP_TOMTOM_PROBABILITY"]) if "VRP_TOMTOM_PROBABILITY" in os.environ else 0.2
    for i in range(max_profiles):

        profiles = os.environ["VRP_PROFILES"].split(",") if "VRP_PROFILES" in os.environ else ["car"]

        vehicle_type = {"type_id": "t{}".format(i), "profile": random.choice(profiles)}
        if random.random() < vrp_tomtom_probability and vehicle_type["profile"] not in [
            "truck",
            "bike",
        ]:  # ensure that your requesting profiles are enabled for tomtom matrix, if not include them here
            vehicle_type["network_data_provider"] = "tomtom"
            vehicle_type["consider_traffic"] = True
        vehicle_types.append(vehicle_type)

        vehicle = {
            "vehicle_id": "vehicle-{}".format(i),
            "type_id": "t{}".format(i),
            "start_address": get_random_location("vehicle-{}".format(i)),
        }
        vehicles.append(vehicle)
    return vehicles, vehicle_types


def get_random_location(name):
    return {
        "location_id": name,
        "lon": random.uniform(13.347702, 13.437996),
        "lat": random.uniform(52.522906, 52.561958),
    }


def get_random_services(max_locations):
    services = []
    for i in range(max_locations):
        services.append(
            {"id": "s{}".format(i), "address": get_random_location("l-{}".format(i))}
        )
    return services
