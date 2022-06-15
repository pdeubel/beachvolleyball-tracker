from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Player(db.Model, UserMixin):

    __tablename__ = "player"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=True)  # Filled in by the user

    def __repr__(self):
        if repr(self.username) is None:
            return f"<User {repr(self.email)}>"
        return f"<User {repr(self.username)}>"

    def get_id(self):
        return str(self.user_id)


class Game(db.Model):

    __tablename__ = "game"

    game_id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"<Game #{repr(self.game_id)}>"

    def get_id(self):
        return str(self.game_id)


class PlayersInGame(db.Model):

    __tablename__ = "players_in_game"


