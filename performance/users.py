from random import uniform

from locust import HttpUser, task, between


class APIUser(HttpUser):
    host = "http://localhost:80"
    wait_time = between(1, 5)

    @task
    def request_prediction(self):
        payload = {
            "x": uniform(-2, 2),
            "y": uniform(-2, 2),
        }
        with self.client.post("/predict", json=payload, catch_response=True) as response:
            try:
                if response.status_code == 200 and "prediction" in response.json():
                    response.success()
                else:
                    response.failure()
            except Exception as e:
                response.failure(e)
