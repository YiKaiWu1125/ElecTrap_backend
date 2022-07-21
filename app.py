#!/usr/bin/env python
from flask import Flask, render_template, Response, request

import mediapipe_processor

Camera = mediapipe_processor.Camera

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('demo.html')


def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/', methods=['POST'])
def pose():
    Camera.processor.change_sol(request.values['pose'])
    return render_template('demo.html')


@app.route('/video_feed')
def video_feed():
    if Camera.processor is None:
        return None
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
