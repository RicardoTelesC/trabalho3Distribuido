"""
Cenário 3: requisição GET na página do post com imagem ~300 KB.
"""
import os

from locust import HttpUser, between, task


POST_PATH = os.environ.get("POST_PATH", "/?p=4")


class WebsiteUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def ver_post_imagem_300kb(self):
        self.client.get(POST_PATH, name="cenario3_post_imagem_300kb")
