from flask import Flask, render_template, Response
from core.camera import VideoCamera

app = Flask(__name__)
cam = VideoCamera()

@app.route('/')
def index():
    return render_template('index.html', alert_text=cam.get_alerts())

@app.route('/video')
def video():
    return Response(cam.generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alert')
def alert():
    return cam.get_alerts()

@app.route('/toggle')
def toggle():
    cam.toggle_streaming()
    return "OK"

@app.route('/mode')
def mode():
    cam.toggle_mode()
    return "OK"

@app.route('/snapshot')
def snapshot():
    path = cam.save_snapshot()
    return f"Snapshot saved: {path}" if path else "No frame"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
