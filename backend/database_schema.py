from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Player(db.Model, UserMixin):

    __tablename__ = "player"

    player_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    player_name = db.Column(db.String(80), nullable=True)  # Filled in by the user
    pin_confirmation_url_part = db.Column(db.String(24), nullable=True)  # Variable generated route for confirmation
    pin_code_hash = db.Column(db.String(200), nullable=True)  # Use hashed 6-Digit Pin for the login
    pin_code_timestamp = db.Column(db.DateTime, nullable=True)  # Timestamp to check if PIN is still valid

    def __repr__(self):
        if repr(self.player_name) is None:
            return f"<User {repr(self.email)}>"
        return f"<User {repr(self.player_name)}>"

    def get_id(self):
        return str(self.player_id)


class Game(db.Model):

    __tablename__ = "game"

    game_id = db.Column(db.Integer, primary_key=True)
    team_0_won = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<Game #{repr(self.game_id)} -- Team {1 if self.team_0_won else 2} won>"

    def get_id(self):
        return str(self.game_id)


class GamesAndPlayers(db.Model):

    __tablename__ = "players_in_game"

    games_and_players_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.game_id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("player.player_id"), nullable=False)
    team = db.Column(db.Boolean, nullable=False)
