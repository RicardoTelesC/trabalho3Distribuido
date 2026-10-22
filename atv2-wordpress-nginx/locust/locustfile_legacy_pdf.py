# API antiga do Locust (exemplo do PDF). Use com imagem grubykarol/locust.
from locust import HttpLocust, TaskSet, task


class UserTasks(TaskSet):
    @task
    def index(self):
        self.client.get("/?p=2")


class WebsiteUser(HttpLocust):
    task_set = UserTasks
    min_wait = 500
    max_wait = 1500
