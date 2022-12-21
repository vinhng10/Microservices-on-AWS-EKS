from random import uniform

from locust import HttpUser, LoadTestShape, task, between


class APIUser(HttpUser):
    wait_time = between(5, 10)

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


class BaseTest(LoadTestShape):

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                try:
                    tick_data = (stage["users"], stage["spawn_rate"], stage["user_classes"])
                except:
                    tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None


class StressTest(BaseTest):
    """ 
    Stress Testing.

    Parameters
    ----------
    BaseTest : LoadTestShape
    
    """
    stages = [
        {"duration": 10, "users": 10, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 30, "users": 50, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 60, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 120, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
    ]


class SpikeTest(BaseTest):
    """
    Spike Testing.

    Parameters
    ----------
    BaseTest : LoadTestShape
    
    """
    stages = [
        {"duration": 10, "users": 10, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 30, "users": 50, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 60, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 120, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
    ]


class LoadTest(BaseTest):
    """
    Load Testing.

    Parameters
    ----------
    BaseTest : LoadTestShape
    
    """
    stages = [
        {"duration": 10, "users": 10, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 30, "users": 50, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 60, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 120, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
    ]


class SoakTest(BaseTest):
    """
    Soak Testing.

    Parameters
    ----------
    BaseTest : LoadTestShape

    """
    stages = [
        {"duration": 10, "users": 10, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 30, "users": 50, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 60, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
        {"duration": 120, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
    ]