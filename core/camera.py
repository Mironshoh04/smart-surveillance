import cv2
from ultralytics import YOLO

class VideoCamera:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.cap = cv2.VideoCapture(0)  # Logitech C920

    def generate(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                break

            results = self.model.track(source=frame, persist=True, classes=[0], stream=True)

            for result in results:
                annotated = result.plot()
                _, buffer = cv2.imencode('.jpg', annotated)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
