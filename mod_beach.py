import os

import click
from flask import Flask

from routes.game import game_page


def create_app():
    from backend.database_schema import db, migrate
    from backend.mail import mail
    from routes.login import login_page, login_manager
    from routes.player import player_page

    app = Flask(__name__)

    secret_key = os.getenv("SECRET_KEY")

    if secret_key is None:
        raise RuntimeError("'SECRET_KEY' environment variable not set, which is required!")

    app.config["SECRET_KEY"] = secret_key

    # Setup of the database settings

    # Postgres on Heroku sets DATABASE_URL to the correct address, alternatively use a local test setup
    default_database_path = "postgresql://postgres:12345678@localhost:5432/local_db"

    database_uri = os.getenv("DATABASE_URL")

    if database_uri is not None:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri.replace("://", "ql://", 1)
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = default_database_path

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Setup of the mail server settings

    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    if app.config["DEBUG"] and (mail_username is None or mail_password is None):
        raise RuntimeError("'MAIL_USERNAME' or 'MAIL_PASSWORD' is not set which is required so that the PIN code "
                           "emails can be sent.")

    # Use the Mailgun add-on from heroku, which like Postgres works with environment variables
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "localhost")
    app.config["MAIL_PORT"] = os.getenv("MAIL_PORT", "25")
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", mail_username)
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", mail_password)
    app.config["MAIL_USE_TLS"] = True

    # Database app initialization
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask Login app initialization
    login_manager.init_app(app)

    # Initialize Flask-Mailman to send mails
    mail.init_app(app)

    beach_location_latitude = os.getenv("BEACH_LOC_LATITUDE")
    beach_location_longitude = os.getenv("BEACH_LOC_LONGITUDE")
    allowed_distance_in_meter = os.getenv("ALLOWED_DISTANCE_METER")

    assert beach_location_latitude is not None and beach_location_longitude is not None, ("Did not set the latitude "
                                                                                          "and longitude positions for "
                                                                                          "the location of the "
                                                                                          "beachvolleyball court!")

    assert allowed_distance_in_meter is not None, ("Please set the allowed distance from the beachvolleyball court in "
                                                   "meters.")

    # Register Blueprints
    app.register_blueprint(login_page)
    app.register_blueprint(player_page)
    app.register_blueprint(game_page)

    return app


@click.command()
@click.option("-d", "--debug", is_flag=True, default=False)
@click.option("-h", "--host", type=str, default=None)
@click.option("--cert", type=str, default=None)
@click.option("--key", type=str, default=None)
def main(debug, host, cert, key):

    app = create_app()

    # XOR: assert that cert and key are either both None or both set
    if (cert is None) ^ (key is None):
        raise RuntimeError("If you provide either --cert or --key, please also provide the other argument!")

    if cert is not None:
        ssl_context = (cert, key)
    else:
        ssl_context = None

    # TODO: add cli param to maybe disable geolocation check when debugging
    app.run(
        debug=debug,
        host=host,
        ssl_context=ssl_context
    )


if __name__ == "__main__":
    main()
