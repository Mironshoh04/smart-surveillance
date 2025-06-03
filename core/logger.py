from collections import defaultdict
import time
import datetime

class AnalyticsLogger:
    def __init__(self):
        self.track_history = set()
        self.last_alert = ""
        self.last_alert_time = 0
        self.reset()

    def reset(self):
        self.people_count = 0
        self.alert_count = 0
        self.hourly_distribution = defaultdict(int)
        self.track_history.clear()

    def log_person(self):
        now = datetime.datetime.now()
        self.people_count += 1
        self.hourly_distribution[now.hour] += 1

    def log_alert(self, message):
        now = time.time()
        if message != self.last_alert or now - self.last_alert_time > 10:
            self.alert_count += 1
            self.last_alert = message
            self.last_alert_time = now

    def summary(self):
        peak_hour = max(self.hourly_distribution, key=self.hourly_distribution.get, default=None)
        return {
            "people_today": self.people_count,
            "alerts": self.alert_count,
            "peak_hour": f"{peak_hour}:00" if peak_hour is not None else "N/A"
        }
