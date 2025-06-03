import cv2
from ultralytics import YOLO
from core.detector import BehaviorEngine


class VideoCamera:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.cap = cv2.VideoCapture(0)  # Logitech C920
        self.behavior = BehaviorEngine()
        self.alert_text = ""

    def generate(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                break

            results = self.model.track(source=frame, persist=True, classes=[0], stream=True, tracker="botsort.yaml")

            for result in results:
                annotated = result.plot()

                # ✅ Extract and analyze tracks for alert logic
                tracks = result.boxes
                if hasattr(tracks, "id") and tracks.id is not None:
                    alerts = self.behavior.update(tracks)
                    self.alert_text = ' | '.join(alerts)

                # Encode annotated frame to JPEG
                _, buffer = cv2.imencode('.jpg', annotated)
                frame_bytes = buffer.tobytes()

                # Yield frame for MJPEG stream
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def get_alerts(self):
        return self.alert_text if hasattr(self, "alert_text") else ""
