"""
Cenário 2: requisição GET na página do post com texto ~400 KB.
"""
import os

from locust import HttpUser, between, task


POST_PATH = os.environ.get("POST_PATH", "/?p=3")


class WebsiteUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def ver_post_texto_400kb(self):
        self.client.get(POST_PATH, name="cenario2_post_texto_400kb")
