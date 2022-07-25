from flask import Blueprint, render_template
from flask_login import login_required
import pandas as pd

from backend.database_schema import GamesAndPlayers, Game, Player

standings_page = Blueprint("standings", __name__)


# TODO if the requests are too frequent, schedule the updating of the standings in a global dict, then display
#   the cached standings, so that each request to /standings does not trigger database queries
# import atexit
# from apscheduler.schedulers.background import BackgroundScheduler
# standings_update_scheduler = BackgroundScheduler()
# standings_update_scheduler.add_job(update_standings, "interval", minutes=5)

# standings_update_scheduler.start()

# Shut down the scheduler when exiting the app
# atexit.register(lambda: standings_update_scheduler.shutdown())


@standings_page.route("/standings", methods=["GET"])
@login_required
def standings():
    all_games = GamesAndPlayers.query.join(
        Game, GamesAndPlayers.game_id == Game.game_id
    ).filter(
        Game.team_1_won.isnot(None)
    ).join(
        Player, GamesAndPlayers.player_id == Player.player_id
    ).with_entities(
        GamesAndPlayers.player_id, GamesAndPlayers.game_id, GamesAndPlayers.team, Game.team_1_won, Player.player_name
    ).group_by(
        GamesAndPlayers.player_id, GamesAndPlayers.game_id, GamesAndPlayers.team, Game.team_1_won, Player.player_name
    ).all()

    standings_raw_data = pd.DataFrame(all_games)
    num_games_per_player = standings_raw_data.groupby("player_id").size().reset_index(name="Games")
    num_won_games_per_player = standings_raw_data[standings_raw_data["team"] == standings_raw_data["team_1_won"]].groupby("player_id").size().reset_index(name="Won")

    standings_dataframe = pd.merge(num_games_per_player, num_won_games_per_player, on="player_id")
    player_names = standings_raw_data[["player_id", "player_name"]].set_index("player_id").drop_duplicates()

    standings_dataframe["player_id"] = standings_dataframe["player_id"].map(player_names["player_name"])
    standings_dataframe = standings_dataframe.rename({"player_id": "Name"}, axis=1).sort_values(by="Won", ascending=False)

    return render_template("standings.html", standings_dataframe=standings_dataframe)