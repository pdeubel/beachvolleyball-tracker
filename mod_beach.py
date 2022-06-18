import os

from flask import Flask


def create_app():
    from backend.database_schema import db, migrate
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

    # Use the Mailgun add-on from heroku, which like Postgres works with environment variables
    app.config["MAIL_SERVER"] = os.getenv("MAILGUN_SMTP_SERVER", "localhost")
    app.config["MAIL_PORT"] = os.getenv("MAILGUN_SMTP_PORT", "25")
    app.config["MAIL_USERNAME"] = os.getenv("MAILGUN_SMTP_LOGIN", "mailuser@localhost")
    app.config["MAIL_PASSWORD"] = os.getenv("MAILGUN_SMTP_PASSWORD", "123456")

    # Database app initialization
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask Login app initialization
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(login_page)
    app.register_blueprint(player_page)

    return app


def main():

    app = create_app()

    """
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    mail = Mail()
    mail.init_app(app)
    """


    # db = SQLAlchemy(app)
    # migrate = Migrate(app, db)

    app.run(debug=True)


if __name__ == "__main__":
    main()
