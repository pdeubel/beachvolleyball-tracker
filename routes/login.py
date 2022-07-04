import time
from datetime import datetime, timedelta
from random import randint, choice
from string import ascii_uppercase, ascii_lowercase, digits
from urllib.parse import urljoin

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, LoginManager, current_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import EmailField, validators, StringField, HiddenField

from backend.database_schema import db, Player, EmailWhitelist
from backend.mail import send_pin_code

login_page = Blueprint("login", __name__)
valid_pin_code_timedelta = timedelta(minutes=15)

login_manager = LoginManager()
login_manager.login_view = "login.login"
login_manager.login_message = "Bitte mit deiner E-Mail einloggen!"


class LoginForm(FlaskForm):
    email = EmailField("E-Mail")


class PinForm(FlaskForm):
    email = HiddenField("E-Mail")
    pin = StringField("Pin Code", validators=[validators.Length(min=6, max=6)])


def generate_pin_confirmation_url_part():
    return "".join(choice(ascii_uppercase + ascii_lowercase + digits) for _ in range(24))


@login_manager.user_loader
def load_player(player_id):
    return Player.query.filter_by(player_id=player_id).first()


@login_page.route("/test-geo", methods=["GET"])
def test_geo():
    return render_template("check_email.html")


@login_page.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("player.player_site"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data

        player: Player = Player.query.filter_by(email=email).first()

        whitelist_approved = EmailWhitelist.query.filter_by(email=email).first()

        if whitelist_approved is None:
            flash("Diese E-Mail ist nicht freigeschaltet, bitte an Patrick wenden!")
            return redirect(request.url)

        if player is None:
            player = Player(
                email=email
            )
            db.session.add(player)
            db.session.commit()

        pin_code = str(randint(100000, 999999))

        already_exist = True
        pin_confirmation_url_part = None

        while already_exist is not None or pin_confirmation_url_part is None:
            pin_confirmation_url_part = generate_pin_confirmation_url_part()
            already_exist = Player.query.filter_by(pin_confirmation_url_part=pin_confirmation_url_part).first()

        player.pin_code_hash = generate_password_hash(pin_code)
        player.pin_code_timestamp = datetime.fromtimestamp(time.time())
        player.pin_confirmation_url_part = pin_confirmation_url_part
        db.session.commit()

        # TODO fill in this function
        send_pin_code(email, pin_code, pin_confirmation_url_part)

        return redirect(urljoin(request.base_url, pin_confirmation_url_part))

    return render_template("login.html", form=form)


@login_page.route("/<pin_confirmation_url_part>", methods=["GET", "POST"])
def validate_pin(pin_confirmation_url_part: str):
    valid_player: Player = Player.query.filter_by(pin_confirmation_url_part=pin_confirmation_url_part).first()

    if valid_player is None:
        # The pin_confirmation_url_part is unique and if it is not found, redirect to the login page
        return redirect(url_for("login.login"))

    form = PinForm()
    form.email.data = valid_player.email

    if form.validate_on_submit():
        current_time = datetime.fromtimestamp(time.time())

        # Check if the Pin code was created less than 15 minutes ago
        pin_code_time_valid = (current_time - valid_player.pin_code_timestamp) < valid_pin_code_timedelta

        if not pin_code_time_valid:
            flash("Der Pin Code ist abgelaufen, bitte erneut einloggen!")
            return redirect(url_for("login.login"))

        pin = form.pin.data
        pin_valid = check_password_hash(valid_player.pin_code_hash, pin)

        if not pin_valid:
            flash("Der Pin Code ist falsch, bitte erneut versuchen!")
            # Reload page
            return redirect(request.url)

        # remember=True keeps player logged in, by default the REMEMBER_COOKIE_DURATION is set to 365 days which should
        # be enough
        login_user(valid_player, remember=True)
        return redirect(url_for("player.player_site"))

    return render_template("pin.html", form=form, pin_confirmation_url_part=pin_confirmation_url_part)
