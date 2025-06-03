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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
