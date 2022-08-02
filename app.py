#!/usr/bin/env python
from flask import Flask, render_template, Response, request

import maze_video_processor

Camera = maze_video_processor.Camera

app = Flask(__name__)


@app.route('/')
def index():
    """index page."""
    return render_template('index.html')

@app.route('/demo')
def test():
    """Video streaming home page."""
    return render_template('demo.html')

@app.route('/gamemode')
def gamemode():
    """ Select gamemode page."""
    return render_template('gamemode.html')

@app.route('/rank')
def rank():
    """ View Score Board page."""
    return render_template('rank.html')



def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/', methods=['POST'])
def pose():
    Camera.playvideo_and_getcoordinate.change_sol(request.values['pose'])
    return render_template('demo.html')


@app.route('/video_feed')
def video_feed():
    if Camera.playvideo_and_getcoordinate is None:
        return None
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
