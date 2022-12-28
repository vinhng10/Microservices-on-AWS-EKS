from locust import LoadTestShape
from performance.users import APIUser


class StressTest(LoadTestShape):
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
    stages =  [
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

