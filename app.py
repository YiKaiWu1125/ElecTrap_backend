#!/usr/bin/env python
import psycopg2
import redis

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, Response, request, flash

import maze_video_processor

Camera = maze_video_processor.Camera

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:8543abcd@localhost/ElecTrap_scoreboard'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)

con = psycopg2.connect(database="ElecTrap_scoreboard", user="postgres", password="8543abcd", host="127.0.0.1", port="5432")
cursor = con.cursor()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class UserInfo(db.Model):
    __tablename__ = 'userinfo'
    user_id = db.Column(db.Integer, primary_key =True)
    user_name = db.Column(db.String(20))
    game_mode = db.Column(db.String(20))
    game_body = db.Column(db.String(20))
    game_level = db.Column(db.Integer)
    score = db.Column(db.Integer)

    def __init__(self,user_name, game_mode, game_body, game_level, score):
        self.user_name = user_name
        self.game_mode = game_mode
        self.game_body = game_body
        self.game_level = game_level
        self.score = score 

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

@app.route("/rank", methods=['post', 'get'])
def rank():  
    cursor.execute("SELECT * FROM userinfo WHERE game_mode='warmup' ORDER BY score ASC LIMIT 10;")
    result = cursor.fetchall()
    return render_template("rank.html", data=result)

@app.route("/getselectinfo", methods=['post','get'])
def getselectinfo():
    mode = request.form["game_mode"]
    body = request.form["game_body"]
    level = request.form["game_level"]
    # FIXME: May cause SQL injection
    cursor.execute("SELECT * FROM userinfo WHERE userinfo.game_mode='{}' AND userinfo.game_body='{}' AND userinfo.game_level={} ORDER BY score ASC LIMIT 10;".format(mode,body,level))
    result = cursor.fetchall()
    return render_template("rank.html", data =result)

@app.route('/getusername', methods=['POST'])
def getusername():
    user_name = request.form["user_name"]
    r.set('user_name',user_name)
    print(user_name)
    return render_template("gamemode.html")

@app.route('/getgameinfo', methods=['POST'])
def getgameinfo():
    name = r.get('user_name')
    game_mode = request.form["game_mode"]
    game_body = request.form["game_body"]
    game_level = request.form["game_level"]
    entry = UserInfo(name, game_mode, game_body, game_level,1000)
    db.session.add(entry)
    db.session.commit()
    print(game_mode, game_body, game_level)

    return render_template("demo.html")

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
    db.create_all()
    app.run(host='0.0.0.0', threaded=True)
