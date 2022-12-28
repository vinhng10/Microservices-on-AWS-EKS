from locust import LoadTestShape
from performance.users import APIUser


class SoakTest(LoadTestShape):
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