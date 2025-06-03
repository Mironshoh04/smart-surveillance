import cv2
from ultralytics import YOLO
from core.detector import BehaviorEngine


class VideoCamera:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.cap = cv2.VideoCapture(0)  # Logitech C920
        self.behavior = BehaviorEngine()
        self.alert_text = ""
        self.streaming = True
        self.detection_enabled = True
        self.last_frame = None

    def generate(self):
        while True:
            if not self.streaming:
                continue  # Skip if paused

            success, frame = self.cap.read()
            if not success:
                break

            self.last_frame = frame.copy()

            if self.detection_enabled:
                results = self.model.track(source=frame, persist=True, classes=[0], stream=True, tracker="botsort.yaml")
                for result in results:
                    annotated = result.plot()
                    tracks = result.boxes
                    if hasattr(tracks, "id") and tracks.id is not None:
                        alerts = self.behavior.update(tracks)
                        self.alert_text = ' | '.join(alerts)
                    frame = annotated

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def get_alerts(self):
        return self.alert_text if hasattr(self, "alert_text") else ""
    
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
