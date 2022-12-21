from random import uniform

from locust import HttpUser, LoadTestShape, task, between


class APIUser(HttpUser):
    host = ""
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

    Use this test to:
        - Determine how the system will behave under extreme conditions
        - Determine what is the maximum capacity of the system in term of users
          or throughput
        - Determine the breaking point of the system and its failure mode
        - Determine if the system will recover without manual intervention after
          the stress test is over

    Parameters
    ----------
    BaseTest : LoadTestShape
    
    """
    stages = [
        # Below normal load:
        {"duration": 10, "users": 10, "spawn_rate": 10, "user_classes": [APIUser]},
        # Normal load:
        {"duration": 30, "users": 50, "spawn_rate": 10, "user_classes": [APIUser]},
        # Around breaking point:
        {"duration": 50, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
        # Beyond breaking point:
        {"duration": 70, "users": 100, "spawn_rate": 10, "user_classes": [APIUser]},
        # Scale down; Recovery stage:
        {"duration": 100, "users": 0, "spawn_rate": 10, "user_classes": [APIUser]},
    ]


class SpikeTest(BaseTest):
    """
    Spike Testing.

    Use this test to:
        - Determine how the system will perform under a sudden surge of traffic
        - Determine if your system will recover once the traffic has subsided

    Parameters
    ----------
    BaseTest : LoadTestShape
    
    """
    stages = [
        # Warm up the system:
        {"duration": 10, "users": 10, "spawn_rate": 10, "user_classes": [APIUser]},
        # Spike load:
        {"duration": 100, "users": 1000, "spawn_rate": 500, "user_classes": [APIUser]},
        # Scale down; Recovery stage:
        {"duration": 120, "users": 10, "spawn_rate": 500, "user_classes": [APIUser]},
        {"duration": 130, "users": 0, "spawn_rate": 10, "user_classes": [APIUser]},
    ]


class LoadTest(BaseTest):
    """
    Load Testing.

    Use this test to:
        - Determine the current performance of the system under typical and peak load
        - Make sure the system is continuously meeting the performance standards
          as there are updates to the system

    Parameters
    ----------
    BaseTest : LoadTestShape
    
    """
    stages = [
        # Scale up the traffic:
        {"duration": 20, "users": 200, "spawn_rate": 10, "user_classes": [APIUser]},
        # Stay at peak for some time:
        {"duration": 120, "users": 200, "spawn_rate": 10, "user_classes": [APIUser]},
        # Scale down the traffic:
        {"duration": 140, "users": 0, "spawn_rate": 10, "user_classes": [APIUser]},
    ]


class SoakTest(BaseTest):
    """
    Soak Testing.

    User this test to:
        - Verify that the system doesn't suffer from bugs or memory leaks
        - Verify that expected application restarts won't lose requests
        - Find bugs related to race-conditions that appear sporadically
        - Make sure the database doesn't exhaust the allocated space and stops
        - Make sure logs don't exhaust the allocated disk space
        - Make sure the depending external services don't stop working after a 
          certain amount of requests are exceeded

    Parameters
    ----------
    BaseTest : LoadTestShape

    """
    stages = [
        # Scale up the traffic:
        {"duration": 5, "users": 200, "spawn_rate": 100, "user_classes": [APIUser]},
        # Stay at peak for some time:
        {"duration": 300, "users": 200, "spawn_rate": 10, "user_classes": [APIUser]},
        # Scale down the traffic:
        {"duration": 305, "users": 0, "spawn_rate": 100, "user_classes": [APIUser]},
    ]