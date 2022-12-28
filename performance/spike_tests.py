from locust import LoadTestShape
from performance.users import APIUser


class SpikeTest(LoadTestShape):
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

