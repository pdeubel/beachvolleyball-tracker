import binascii
import json
from base64 import b64decode
from math import ceil

import sqlalchemy.exc
from flask import Blueprint, render_template, request, jsonify, url_for, redirect
from flask_login import login_required, current_user

from backend.database_schema import Player, Game, db, GamesAndPlayers

game_page = Blueprint("game", __name__)


@game_page.route("/game", methods=["GET", "POST"])
@login_required
def game_site():
    return render_template(
        "game_site.html",
        current_player_id=current_user.player_id,
        current_player_name=current_user.player_name
    )


@game_page.route("/game/<game_id>", methods=["GET"])
@login_required
def show_game_with_id(game_id: int):
    return render_template("select_teams.html", game_id=game_id)


@game_page.route("/game/player-lookup", methods=["POST"])
def player_lookup():
    data = request.form["scanned_data"]

    try:
        # str -> bytes -> decode base64 -> bytes -> str
        decoded_data = b64decode(data.encode("ascii")).decode("ascii")
        decoded_data_json = json.loads(decoded_data)
    except binascii.Error or json.decoder.JSONDecodeError:
        # Not base64 encoded data or non valid JSON data
        return "Invalid data", 400

    try:
        player_id = decoded_data_json["player_id"]
        email = decoded_data_json["email"]
    except KeyError:
        # False JSON data
        return "Invalid data", 400

    try:
        player: Player = Player.query.filter_by(player_id=player_id, email=email).first()
    except sqlalchemy.exc.DataError:
        return "Invalid data", 400

    if player is None:
        # Player not found
        return "Invalid data", 400

    answer = {"player_id": player.player_id, "player_name": player.player_name}

    return jsonify(answer)


@game_page.route("/game/select-teams", methods=["POST"])
@login_required
def select_teams():
    if request.method == "POST":
        try:
            players = request.get_json()["players"]
        except json.decoder.JSONDecodeError or KeyError:
            return "Invalid data", 400

        print(f"Players: {players} type {type(players)}")

        index_to_separate_teams = ceil(len(players) / 2)

        return jsonify({"team_1": players[:index_to_separate_teams], "team_2": players[index_to_separate_teams:]})


@game_page.route("/game/create-game", methods=["POST"])
@login_required
def create_game():
    try:
        player_team_map = request.get_json()
    except json.decoder.JSONDecodeError:
        return "Invalid data", 400

    game = Game()
    db.session.add(game)
    db.session.commit()

    for player_id, team in player_team_map.items():
        games_and_players = GamesAndPlayers(
            game_id=game.game_id,
            player_id=player_id,
            team=bool(team)
        )
        db.session.add(games_and_players)

    db.session.commit()

    return redirect(url_for("game.show_game_with_id", game_id=game.game_id))
