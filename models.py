from app import db


class UserInfo(db.Model):
    __tablename__ = 'userinfo'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20))
    game_mode = db.Column(db.String(20))
    game_body = db.Column(db.String(20))
    game_level = db.Column(db.Integer)
    score = db.Column(db.Integer)

    def __init__(self, user_name, game_mode, game_body, game_level, score):
        self.user_name = user_name
        self.game_mode = game_mode
        self.game_body = game_body
        self.game_level = game_level
        self.score = score

    def __repr__(self):
        return f'<User {self.user_name}>: {self.game_mode} {self.game_body} {self.game_level} {self.score}'
