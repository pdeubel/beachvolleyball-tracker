import time
from datetime import datetime, timedelta
from random import randint, choice
from string import ascii_uppercase, ascii_lowercase, digits

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import EmailField, validators, StringField, HiddenField

from backend.database_schema import db, Player
from backend.mail import send_pin_code

login_page = Blueprint("login", __name__)
valid_pin_code_timedelta = timedelta(minutes=1)


class LoginForm(FlaskForm):
    email = EmailField("E-Mail")


class PinForm(FlaskForm):
    email = HiddenField("E-Mail")
    pin = StringField("Pin Code", validators=[validators.Length(min=6, max=6)])


def generate_pin_confirmation_url_part():
    return "".join(choice(ascii_uppercase + ascii_lowercase + digits) for _ in range(24))


@login_page.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data

        player: Player = Player.query.filter_by(email=email).first()

        if player is None:
            """
            1. Check Whitelist
            2. Not in whitelist
                - Error message
            3. In Whitelist
                - Create Player object in database
                - Then continue below with sending pin code
            """
            pass

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

        return render_template("check_email.html")

    return render_template("login.html", form=form)


@login_page.route("/<pin_confirmation_url_part>", methods=["GET", "POST"])
def validate_pin(pin_confirmation_url_part: str):

    # if user is not None and check_password_hash(user.password, password):
    #     login_user(user)
    #
    #     flask.flash("Logged in")

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
            # TODO check if flash message works
            flash("Der Pin Code ist abgelaufen, bitte erneut einloggen!")
            return redirect(url_for("login.login"))

        pin = form.pin.data
        pin_valid = check_password_hash(valid_player.pin_code_hash, pin)

        if not pin_valid:
            flash("Der Pin Code ist falsch, bitte erneut versuchen!")
            return redirect(request.url)


        """
        1. Compare pin from form with hashed pin from database + Check timestamp 15 min
        3. Pin is not equal
            - Error message: Try again
        2. Timestamp > 15min
            - Error message: Pin Code expired, log in again
            - Redirect login page
        4. Pin equal + timestamp <= 15 min
            - Login
        """

    return render_template("pin.html", form=form, pin_confirmation_url_part=pin_confirmation_url_part)
