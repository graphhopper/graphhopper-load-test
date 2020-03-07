from personas import common

from locust import HttpLocust, TaskSet, task


class PersonaTaskSet(TaskSet):
    def on_start(self):
        self.client.verify = False
        self.api_key = common.get_api_key()
        common.setup_locust_debugging()

    @task
    def get_isochrone(self):
        points = ",".join(str(p) for p in common.get_random_berlin_point())
        path = f"/api/1/isochrone?point={points}&key={self.api_key}"
        self.client.get(path, name="Isochrone")


class PersonaIsochrone(HttpLocust):
    task_set = PersonaTaskSet
    weight = 1
