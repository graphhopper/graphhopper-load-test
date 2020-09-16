from personas import common

from locust import TaskSet, task
from locust.contrib.fasthttp import FastHttpLocust
from locust.wait_time import constant_pacing


class PersonaTaskSet(TaskSet):

    def on_start(self):
        self.client.verify = False
        self.api_key_url_suffix = common.get_api_key_url_suffix("&")
        self.points_query = common.get_points_query(self)
        common.setup_locust_debugging()

    @task
    def get_matrix(self):
        base_url = "/route"
        path = f"{base_url}?{self.points_query}{self.api_key_url_suffix}"
        self.client.get(path, name="Matrix", verify=False)


class PersonaMatrix(FastHttpLocust):
    tasks = [PersonaTaskSet]
    weight = 1
    network_timeout = 3.0
    connection_timeout = 3.0
    wait_time = constant_pacing(1.0)
