import os

from flask import Flask
from flask_mailman import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


def setup_app():
    app = Flask(__name__)

    secret_key = os.getenv("SECRET_KEY")

    if secret_key is None:
        raise RuntimeError("'SECRET_KEY' environment variable not set, which is required!")

    app.config["SECRET_KEY"] = secret_key

    # Setup of the database settings

    # Postgres on Heroku sets DATABASE_URL to the correct address, alternatively use a local test setup
    default_database_path = "postgresql://postgres:12345678@localhost:5432/local_db"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", default_database_path)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Setup of the mail server settings

    # Use the Mailgun add-on from heroku, which like Postgres works with environment variables
    app.config["MAIL_SERVER"] = os.getenv("MAILGUN_SMTP_SERVER", "localhost")
    app.config["MAIL_PORT"] = os.getenv("MAILGUN_SMTP_PORT", "25")
    app.config["MAIL_USERNAME"] = os.getenv("MAILGUN_SMTP_LOGIN", "mailuser@localhost")
    app.config["MAIL_PASSWORD"] = os.getenv("MAILGUN_SMTP_PASSWORD", "123456")

    return app


def main():
    app = setup_app()

    """
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    mail = Mail()
    mail.init_app(app)
    """

    app.run()


if __name__ == "__main__":
    main()
