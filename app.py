# app.py
from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from core.camera import VideoCamera
import os

UPLOAD_FOLDER='uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

current_settings={
  "loiter_time": 5,
  "crowd_threshold": 3
}

cam=None

def set_camera(source):
    global cam
    if cam:
        cam.cap.release()
    cam = VideoCamera(source)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize with default webcam
cam = VideoCamera()

@app.route('/')
def index():
    return render_template('index.html', alert_text=cam.get_alerts(), settings=current_settings)

@app.route('/video')
def video():
    return Response(cam.generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/switch', methods=['POST'])
def switch():
    mode = request.form.get('mode')
    if mode == 'camera':
        set_camera(0)
    elif 'video' in request.files:
        file = request.files['video']
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        set_camera(path)
    return redirect(url_for('index'))

@app.route('/settings', methods=['POST'])
def settings():
    current_settings["loiter_time"] = int(request.form['loiter_time'])
    current_settings["crowd_threshold"] = int(request.form['crowd_threshold'])
    cam.behavior.loiter_time = current_settings["loiter_time"]
    cam.behavior.crowd_threshold = current_settings["crowd_threshold"]
    return redirect(url_for('index'))

@app.route('/alert')
def alert():
    return jsonify(cam.get_alerts())

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

@app.route('/status')
def status():
    return {"streaming": cam.streaming}

@app.route('/dashboard')
def dashboard():
    stats = cam.logger.summary()
    return render_template("dashboard.html", stats=stats)

@app.route('/upload', methods=['POST'])
def upload():
    video = request.files.get('video')
    if not video:
        return "No video uploaded", 400
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
    video.save(filepath)
    global cam
    cam = VideoCamera(source=filepath)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
