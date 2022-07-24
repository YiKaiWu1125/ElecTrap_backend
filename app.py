#!/usr/bin/env python
from flask import Flask, render_template, Response, request

import mediapipe_processor

Camera = mediapipe_processor.Camera

app = Flask(__name__)


@app.route('/')
def index():
    """index page."""
    return render_template('index.html')

@app.route('/demo.html')
def test():
    """Video streaming home page."""
    return render_template('demo.html')

@app.route('/bodySelect.html')
def bodymode():
    """Select body mode page."""
    return render_template('bodySelect.html')

@app.route('/foot_levelmap.html')
def foot_levelmap():
    """ Select Foot Level map page."""
    return render_template('foot_levelmap.html')

@app.route('/gamemode.html')
def gamemode():
    """ Select gamemode page."""
    return render_template('gamemode.html')

@app.route('/hands_levelmap.html')
def hands_levelmap():
    """Select Hands Level map page."""
    return render_template('hands_levelmap.html')

@app.route('/head_levelmap.html')
def head_levelmap():
    """ Select Head Level map page."""
    return render_template('head_levelmap.html')

@app.route('/levelmap.html')
def levelmap():
    """ Select level map page."""
    return render_template('levelmap.html')

@app.route('/master.html')
def master_mode():
    """ Select Master mode page."""
    return render_template('master.html')



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
