from flask import Blueprint, render_template
from flask_login import login_required

player_page = Blueprint("player", __name__)


@player_page.route("/player", methods=["GET"])
@login_required
def player_site():
    return render_template("player_site.html")
