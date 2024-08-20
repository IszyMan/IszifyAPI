from flask import Flask
from extensions import db, jwt, migrate, mail, cors
from config import config_obj
from models.users import Users
from models.shorten_url import Urlshort, UrlShortenerClicks, ShortUrlClickLocation
from endpoints import AuthenticationBlueprint, UserBlueprint
from utils import return_response
from http_status import HttpStatus
from status_res import StatusRes


def create_app(config_name="development"):
    app = Flask(__name__)

    app.config.from_object(config_obj[config_name])

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    mail.init_app(app)

    # user loader
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        user_id = jwt_data["sub"]
        return Users.query.get(user_id)

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return return_response(
            HttpStatus.UNAUTHORIZED,
            status=StatusRes.FAILED,
            message="Token Expired",
        )

    @jwt.invalid_token_loader
    def my_invalid_token_callback(jwt_header, jwt_payload):
        return return_response(
            HttpStatus.UNAUTHORIZED,
            status=StatusRes.FAILED,
            message="Invalid Token",
        )

    @jwt.unauthorized_loader
    def my_unauthorized_callback(jwt_header, jwt_payload):
        return return_response(
            HttpStatus.UNAUTHORIZED,
            status=StatusRes.FAILED,
            message="Unauthorized",
        )

    app.register_blueprint(AuthenticationBlueprint, url_prefix="/api/v1")
    app.register_blueprint(UserBlueprint, url_prefix="/api/v1")

    return app
