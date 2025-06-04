from collections import defaultdict, deque
import time
import datetime

class AnalyticsLogger:
    def __init__(self):
        self.track_history = set()
        self.last_alert = ""
        self.last_alert_time = 0
        self.loiter_by_hour = defaultdict(int)
        self.loiter_minute_log = deque(maxlen=60)
        self.reset()

    def reset(self):
        self.people_count = 0
        self.alert_count = 0
        self.hourly_distribution = defaultdict(int)
        self.last_alert = ""
        self.last_alert_time = 0
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

        if "Loitering" in message:
            dt_now = datetime.datetime.now()
            hour = dt_now.hour
            self.loiter_by_hour[hour] += 1

            minute = dt_now.replace(second=0, microsecond=0)
            if self.loiter_minute_log and self.loiter_minute_log[-1][0] == minute:
                self.loiter_minute_log[-1] = (minute, self.loiter_minute_log[-1][1] + 1)
            else:
                self.loiter_minute_log.append((minute, 1))

    def recent_loitering(self, minutes=30):
        cutoff = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        seen = {entry[0]: entry[1] for entry in self.loiter_minute_log if entry[0] >= cutoff}
        labels, values = [], []
        for i in range(minutes):
            t = cutoff + datetime.timedelta(minutes=i)
            labels.append(t.strftime('%H:%M'))
            values.append(seen.get(t.replace(second=0, microsecond=0), 0))
        return labels, values

    def summary(self):
        peak_hour = max(self.hourly_distribution, key=self.hourly_distribution.get, default=None)
        return {
            "people_today": self.people_count,
            "alerts": self.alert_count,
            "peak_hour": f"{peak_hour}:00" if peak_hour is not None else "N/A"
        }

    def loitering_distribution(self, last_n_hours=24):
        return {h: self.loiter_by_hour[h] for h in range(24)[-last_n_hours:]}