from personas import common

from locust import HttpLocust, TaskSet, task


class PersonaTaskSet(TaskSet):

    def on_start(self):
        self.client.verify = False
        self.api_key = common.get_api_key()
        self.points_query = common.get_points_query(self)
        common.setup_locust_debugging()

    @task
    def get_matrix(self):
        base_url = common.get_base_url("matrix")        
        path = f"{base_url}?{self.points_query}&key={self.api_key}"
        self.client.get(path, name="Matrix")


class PersonaMatrix(HttpLocust):
    task_set = PersonaTaskSet
    weight = 1
