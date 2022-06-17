import time
from datetime import datetime
from random import randint

from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash
from wtforms import EmailField, validators, StringField

from backend.database_schema import Player
from backend.mail import send_pin_code

login_page = Blueprint("login", __name__)


class LoginForm(FlaskForm):
    email = EmailField("E-Mail")


class PinForm(FlaskForm):
    pin = StringField("Pin Code", validators=[validators.Length(min=6, max=6)])


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
        player.pin_code = generate_password_hash(pin_code)
        player.pin_code_timestamp = datetime.fromtimestamp(time.time())

        # TODO fill in this function
        send_pin_code(email, pin_code)

        # TODO create pin_login
        pin_form = PinForm()
        return render_template("pin.html", form=pin_form, email=email)

    return render_template("login.html", form=form)


@login_page.route("/pin", methods=["GET", "POST"])
def validate_pin():

    # if user is not None and check_password_hash(user.password, password):
    #     login_user(user)
    #
    #     flask.flash("Logged in")

    form = PinForm()

    if form.validate_on_submit():
        pin = form.pin.data

        print(pin)
        print(f"Type: {type(pin)}")

    login_form = LoginForm()
    return render_template("login.html", form=login_form)




