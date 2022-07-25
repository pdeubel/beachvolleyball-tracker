import os

import click
from flask import Flask

from routes.game import game_page


def create_app():
    from flask_talisman import Talisman

    from backend.database_schema import db, migrate
    from backend.mail import mail
    from routes.login import login_page, login_manager
    from routes.player import player_page
    from routes.standings import standings_page

    app = Flask(__name__)

    # Set up Talisman to force HTTPS; set content_security_policy to None as it otherwise prevents loading of any
    # resources not in the same domain as the web app (e.g. JS libraries etc.)
    Talisman(app, force_https=True, content_security_policy=None)

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

    mail_sender_address = os.getenv("MAIL_SENDER_ADDRESS")
    assert mail_sender_address is not None, "Please specify the E-Mail sender address with 'MAIL_SENDER_ADDRESS'"

    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    assert (mail_username is not None and mail_password is not None), ("'MAIL_USERNAME' and/or 'MAIL_PASSWORD' are not "
                                                                       "set which is required so that the PIN code "
                                                                       "E-mails can be sent.")

    # Use the Mailgun add-on from heroku, which like Postgres works with environment variables
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "localhost")
    app.config["MAIL_PORT"] = os.getenv("MAIL_PORT", "25")
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", mail_username)
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", mail_password)
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "False").lower() in ("true", "1")

    # Database app initialization
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask Login app initialization
    login_manager.init_app(app)

    # Initialize Flask-Mailman to send mails
    mail.init_app(app)

    # Register Blueprints
    app.register_blueprint(login_page)
    app.register_blueprint(player_page)
    app.register_blueprint(game_page)
    app.register_blueprint(standings_page)

    return app


@click.command()
@click.option("-d", "--debug/--no-debug", is_flag=True, default=False)
@click.option("-h", "--host", type=str, default=None)
def main(debug: bool, host: str):

    app = create_app()

    app.run(
        debug=debug,
        host=host,
        ssl_context=("cert.pem", "key.pem")
    )


if __name__ == "__main__":
    main()
