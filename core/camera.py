import cv2
from ultralytics import YOLO
from core.detector import BehaviorEngine
import time
from core.logger import AnalyticsLogger
from collections import deque
import datetime


class VideoCamera:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.cap = cv2.VideoCapture(0)
        self.behavior = BehaviorEngine()
        self.streaming = True
        self.detection_enabled = True
        self.last_frame = None
        self.logger = AnalyticsLogger()
        self.alert_log = deque(maxlen=20)  # store (timestamp, message)

    def generate(self):
        while True:
            if not self.streaming:
                continue

            success, frame = self.cap.read()
            if not success:
                break

            self.last_frame = frame.copy()

            if self.detection_enabled:
                results = self.model.track(source=frame, persist=True, classes=[0], stream=True, tracker="botsort.yaml")
                for result in results:
                    frame = result.plot()
                    tracks = result.boxes
                    if hasattr(tracks, "id") and tracks.id is not None:
                        alerts = self.behavior.update(tracks)

                        now = datetime.datetime.now().strftime('%H:%M:%S')
                        for msg in alerts:
                            self.alert_log.appendleft(f"[{now}] {msg}")
                            self.logger.log_alert(msg)

                        current_ids = [int(tid.item()) for tid in tracks.id]
                        for tid in current_ids:
                            if tid not in self.logger.track_history:
                                self.logger.track_history.add(tid)
                                self.logger.log_person()

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def get_alerts(self):
        return list(self.alert_log)

    def toggle_streaming(self):
        self.streaming = not self.streaming

    def toggle_mode(self):
        self.detection_enabled = not self.detection_enabled

    def save_snapshot(self):
        if self.last_frame is not None:
            filename = f'static/snapshot_{int(time.time())}.jpg'
            cv2.imwrite(filename, self.last_frame)
            return filename
        return None
