from flask import Flask
from extensions import db, jwt, migrate, mail, cors, limiter
from config import config_obj
from models.users import Users
from models.shorten_url import Urlshort, UrlShortenerClicks, ShortUrlClickLocation
from models.blogs import Catgories, Blogs
from models.qrcode import QRCodeCategories, QRCodeData, QrCodeStyling, SocialMedia
from models.qrcode_unauth import QRCodeDataUnauth
from models.payment import PaymentPlans, Subscriptions, Transactions
from models.admin_models import Admin, AdminSession
from models.giftlink import (
    GiftLinks,
    Donation,
    UserWallet,
    SavedBank,
    GiftAccount,
    SocialLinks,
    NicheEnum,
)
from endpoints import (
    AuthenticationBlueprint,
    UserBlueprint,
    BlogBlueprint,
    QRCodeBlueprint,
    RedirectUrlBlueprint,
    UrlShortBlueprint,
    UnauthQRCodeBlueprint,
    AdminAccountBlueprint,
    AdminAuthBlueprint,
    TransactionsBlueprint,
    AnalyticsBlueprint,
    CloudNaryBlueprint,
    GiftlinkBlueprint,
)
from utils import return_response
from http_status import HttpStatus
from status_res import StatusRes
from flask_limiter.errors import RateLimitExceeded
from sqlalchemy.exc import OperationalError
from logger import logger


def create_app(config_name="development"):
    app = Flask(__name__)

    app.config.from_object(config_obj[config_name])

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Authorization", "Content-Type"],
                "supports_credentials": True,
            }
        },
    )

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    limiter.init_app(app)

    # user loader
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        user_id = jwt_data["sub"]
        return Users.query.get(user_id) or Admin.query.get(user_id)

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header=None, jwt_payload=None):
        return return_response(
            HttpStatus.UNAUTHORIZED,
            status=StatusRes.FAILED,
            message="Token Expired",
        )

    @jwt.invalid_token_loader
    def my_invalid_token_callback(jwt_header=None, jwt_payload=None):
        return return_response(
            HttpStatus.UNAUTHORIZED,
            status=StatusRes.FAILED,
            message="Invalid Token",
        )

    @jwt.unauthorized_loader
    def my_unauthorized_callback(jwt_header=None, jwt_payload=None):
        return return_response(
            HttpStatus.UNAUTHORIZED,
            status=StatusRes.FAILED,
            message="Unauthorized",
        )

    # error 404
    @app.errorhandler(404)
    def not_found(e):
        return return_response(
            HttpStatus.NOT_FOUND,
            status=StatusRes.FAILED,
            message="Endpoint Not Found",
        )

    # method not allowed
    @app.errorhandler(405)
    def method_not_allowed(e):
        return return_response(
            HttpStatus.METHOD_NOT_ALLOWED,
            status=StatusRes.FAILED,
            message="Method Not Allowed",
        )

    # 500
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"{e}: internal_server_error")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )

    @app.errorhandler(OperationalError)
    def handle_operational_error(e):
        logger.error(f"{e}: OperationalError")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Connection Error",
        )

    # rate limit exceeded
    @app.errorhandler(RateLimitExceeded)
    def ratelimit_handler(e):
        logger.error(f"{e}: ratelimit@errorhandler")
        return return_response(
            HttpStatus.TOO_MANY_REQUESTS,
            status=StatusRes.FAILED,
            message="Too Many Requests, Please Try Again Later",
        )

    app.register_blueprint(AuthenticationBlueprint, url_prefix="/api/v1")
    app.register_blueprint(UserBlueprint, url_prefix="/api/v1")
    app.register_blueprint(BlogBlueprint, url_prefix="/api/v1")
    app.register_blueprint(QRCodeBlueprint, url_prefix="/api/v1")
    app.register_blueprint(UrlShortBlueprint, url_prefix="/api/v1")
    app.register_blueprint(UnauthQRCodeBlueprint, url_prefix="/api/v1")
    app.register_blueprint(AdminAccountBlueprint, url_prefix="/api/v1")
    app.register_blueprint(AdminAuthBlueprint, url_prefix="/api/v1")
    app.register_blueprint(TransactionsBlueprint, url_prefix="/api/v1")
    app.register_blueprint(AnalyticsBlueprint, url_prefix="/api/v1")
    app.register_blueprint(CloudNaryBlueprint, url_prefix="/api/v1")
    app.register_blueprint(GiftlinkBlueprint, url_prefix="/api/v1")
    app.register_blueprint(RedirectUrlBlueprint)

    return app
