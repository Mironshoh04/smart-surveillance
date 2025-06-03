import time

class BehaviorEngine:
    def __init__(self, loiter_time=5, crowd_threshold=1):
        self.loiter_time = loiter_time
        self.crowd_threshold = crowd_threshold
        self.track_memory = {}  # track_id: (first_seen_time, last_pos)
        self.alerts = []

    def update(self, tracks):
        now = time.time()
        self.alerts = []
        active_ids = set()

        for track in tracks:
            tid = int(track.id)
            x, y, w, h = track.xyxy[0].tolist()
            cx, cy = (x + w) / 2, (y + h) / 2  # center point
            active_ids.add(tid)

            if tid not in self.track_memory:
                self.track_memory[tid] = (now, (cx, cy))
            else:
                first_seen, (px, py) = self.track_memory[tid]
                if abs(cx - px) < 20 and abs(cy - py) < 20:
                    if now - first_seen > self.loiter_time:
                        self.alerts.append(f"Loitering detected (ID {tid})")
                else:
                    self.track_memory[tid] = (now, (cx, cy))

        if len(active_ids) > self.crowd_threshold:
            self.alerts.append(f"Crowd alert: {len(active_ids)} people detected")

        # cleanup old IDs
        for tid in list(self.track_memory):
            if tid not in active_ids:
                del self.track_memory[tid]

        print("🔍 Incoming tracks:", [int(t.id) for t in tracks if t.id is not None])
        print("📊 Track memory keys:", list(self.track_memory.keys()))
        print("🚨 Alerts:", self.alerts)

        return self.alerts
