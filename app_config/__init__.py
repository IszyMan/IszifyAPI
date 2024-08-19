from flask import Flask
from extensions import db, jwt, migrate, mail
from config import config_obj


def create_app(config_name="development"):
    app = Flask(__name__)

    app.config.from_object(config_obj[config_name])

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    return app
