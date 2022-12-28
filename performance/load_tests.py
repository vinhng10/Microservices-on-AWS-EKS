from locust import LoadTestShape
from performance.users import APIUser


class LoadTest(LoadTestShape):
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
