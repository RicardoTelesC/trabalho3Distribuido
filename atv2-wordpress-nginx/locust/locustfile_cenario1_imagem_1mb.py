"""
Cenário 1: requisição GET na página do post com imagem ~1 MB.
Configure POST_ID (query ?p=) via variável de ambiente POST_ID ou no comando Locust.
"""
import os

from locust import HttpUser, between, task


POST_PATH = os.environ.get("POST_PATH", "/?p=2")


class WebsiteUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def ver_post_imagem_1mb(self):
        self.client.get(POST_PATH, name="cenario1_post_imagem_1mb")
