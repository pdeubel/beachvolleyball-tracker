import binascii
import json
import os
import time
from base64 import b64decode
from datetime import datetime
from math import ceil

import sqlalchemy.exc
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, session, current_app
from flask_login import login_required, current_user

from backend.database_schema import Player, Game, db, GamesAndPlayers

game_page = Blueprint("game", __name__)

beach_location_latitude = os.getenv("BEACH_LOC_LATITUDE")
beach_location_longitude = os.getenv("BEACH_LOC_LONGITUDE")
allowed_distance_in_meter = os.getenv("ALLOWED_DISTANCE_METER")
minimum_players_per_game = os.getenv("MINIMUM_PLAYERS_PER_GAME", 2)


@game_page.route("/game", methods=["GET", "POST"])
@login_required
def game_site():
    if request.method == "GET":
        try:
            location_in_radius = session["location_in_radius"]
            location_in_radius_timestamp = session["location_in_radius_timestamp"]
        except KeyError:
            return render_template("error_geolocation.html")
        else:
            # Was the timestamp longer than 15 minutes (900s) ago?
            timed_out = (time.time() - location_in_radius_timestamp) > 900

            if timed_out:
                return render_template(
                    "check_geolocation.html",
                    beach_location_latitude=beach_location_latitude,
                    beach_location_longitude=beach_location_longitude,
                    allowed_distance_in_meter=allowed_distance_in_meter
                )

            if location_in_radius:
                return render_template(
                    "game_site.html",
                    current_player_id=current_user.player_id,
                    current_player_name=current_user.player_name,
                    minimum_players_per_game=minimum_players_per_game
                )
            else:
                return render_template("error_geolocation.html")
    else:
        try:
            location_in_radius = request.form["location_in_radius"]
        except KeyError:
            # Only check for geolocation when not debugging
            if not current_app.config["DEBUG"]:
                return render_template(
                    "check_geolocation.html",
                    beach_location_latitude=beach_location_latitude,
                    beach_location_longitude=beach_location_longitude,
                    allowed_distance_in_meter=allowed_distance_in_meter
                )

            # Since we are debugging simply say we are in location. Facilitates different device debugging
            location_in_radius = "true"

        session["location_in_radius_timestamp"] = time.time()

        if location_in_radius == "true":
            session["location_in_radius"] = True
            return render_template(
                "game_site.html",
                current_player_id=current_user.player_id,
                current_player_name=current_user.player_name,
                minimum_players_per_game=minimum_players_per_game
            )
        else:
            session["location_in_radius"] = False
            return render_template("error_geolocation.html")


@game_page.route("/game/<game_id>", methods=["GET"])
@login_required
def show_game_with_id(game_id: int):
    game = Game.query.filter_by(game_id=game_id).first()

    # Only the creator has access to the game page and only if no result has been added
    if (game is None
            or game.game_created_by != current_user.player_id
            or game.win_result_submitted_timestamp is not None
            or game.team_1_won is not None):
        return redirect(url_for("player.player_site"))

    players = Player.query.join(GamesAndPlayers).filter_by(game_id=game_id)
    # Team set to False (or as integer '0') resembles Team 1
    first_team_player_names = [p.player_name for p in players.filter_by(team=False).all()]
    second_team_player_names = [p.player_name for p in players.filter_by(team=True).all()]

    return render_template("select_winner_team.html", game_id=game_id, first_team_player_names=first_team_player_names,
                           second_team_player_names=second_team_player_names)


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

        if len(players) < minimum_players_per_game:
            # 403 Forbidden -> This should only occur if someone modified the DOM to enable the button
            return "Not enough players", 403

        index_to_separate_teams = ceil(len(players) / 2)

        return jsonify({"team_1": players[:index_to_separate_teams], "team_2": players[index_to_separate_teams:]})


@game_page.route("/game/create-game", methods=["POST"])
@login_required
def create_game():
    try:
        player_team_map = request.get_json()
    except json.decoder.JSONDecodeError:
        return "Invalid data", 400

    game = Game(
        game_created_by=current_user.player_id,
        game_created_timestamp=datetime.fromtimestamp(time.time())
    )
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


@game_page.route("/game/register-winner", methods=["POST"])
@login_required
def register_game_winner():
    game_id = int(request.form["game_id"])
    winner_team = request.form["winner_team"]

    game = Game.query.filter_by(game_id=game_id).first()

    if game.team_1_won is None:
        game.team_1_won = bool(winner_team)
        game.win_result_submitted_timestamp = datetime.fromtimestamp(time.time())
        db.session.commit()

    return ("Success", 201)


@game_page.route("/game/minimum-players", methods=["GET"])
@login_required
def return_minimum_players_per_game():
    return jsonify({"minimum_players_per_game": minimum_players_per_game})
