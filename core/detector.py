import time

class BehaviorEngine:
    def __init__(self, loiter_time=5, crowd_threshold=3):
        self.loiter_time = loiter_time
        self.crowd_threshold = crowd_threshold
        self.track_memory = {}  # track_id: (first_seen_time, last_position)
        self.loitering_ids = set()  # to suppress duplicate loiter alerts
        self.last_crowd_alert_time = 0  # timestamp for last crowd alert
        self.alerts = []

    def update(self, tracks):
        now = time.time()
        self.alerts = []
        active_ids = set()

        for track in tracks:
            tid = int(track.id)
            x, y, w, h = track.xyxy[0].tolist()
            cx, cy = (x + w) / 2, (y + h) / 2
            active_ids.add(tid)

            if tid not in self.track_memory:
                self.track_memory[tid] = (now, (cx, cy))
            else:
                first_seen, (px, py) = self.track_memory[tid]
                if abs(cx - px) < 20 and abs(cy - py) < 20:
                    if now - first_seen > self.loiter_time and tid not in self.loitering_ids:
                        self.alerts.append(f"Loitering detected (ID {tid})")
                        self.loitering_ids.add(tid)
                else:
                    self.track_memory[tid] = (now, (cx, cy))

        if len(active_ids) > self.crowd_threshold:
            if now - self.last_crowd_alert_time > 30:
                self.alerts.append(f"Crowd alert: {len(active_ids)} people detected")
                self.last_crowd_alert_time = now

        # Cleanup: remove old track IDs not seen anymore
        for tid in list(self.track_memory.keys()):
            if tid not in active_ids:
                del self.track_memory[tid]
                self.loitering_ids.discard(tid)  # allow re-detection if they come back later

        return self.alerts
