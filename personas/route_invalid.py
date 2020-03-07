import random
from locust import HttpLocust, TaskSet, task

from personas import common


class PersonaTaskSet(TaskSet):
    def on_start(self):
        self.client.verify = False
        self.api_key = common.get_api_key()
        common.setup_locust_debugging()

    @task
    def get_route(self):
        points = ["{:.2f}".format(random.uniform(20.0, 80.0)) for _ in range(4)]
        path = f"/api/1/route?point={points[0]}%2C{points[1]}&point={points[2]}%2C{points[3]}&key={self.api_key}"
        self.client.get(path, name="Route erratic")


class PersonaRouteInvalid(HttpLocust):
    task_set = PersonaTaskSet
    weight = 1
    # min_wait = 500
    # max_wait = 700
