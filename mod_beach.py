import os

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
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", default_database_path)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Setup of the mail server settings

    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    if mail_username is None or mail_password is None:
        raise RuntimeError("'MAIL_USERNAME' or 'MAIL_PASSWORD' is not set which is required so that the PIN code "
                           "emails can be sent.")

    # Use the Mailgun add-on from heroku, which like Postgres works with environment variables
    app.config["MAIL_SERVER"] = os.getenv("MAILGUN_SMTP_SERVER", "localhost")
    app.config["MAIL_PORT"] = os.getenv("MAILGUN_SMTP_PORT", "25")
    app.config["MAIL_USERNAME"] = os.getenv("MAILGUN_SMTP_LOGIN", mail_username)
    app.config["MAIL_PASSWORD"] = os.getenv("MAILGUN_SMTP_PASSWORD", mail_password)

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


def main():

    app = create_app()

    # TODO: add cli parameter for host and ssl_context and maybe disable geolocation check when debugging
    app.run(
        debug=True,
        # host="192.168.178.29",
        # ssl_context=("cert.pem", "key.pem")
    )


if __name__ == "__main__":
    main()
