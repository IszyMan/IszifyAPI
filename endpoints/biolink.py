from flask import Blueprint
from http_status import HttpStatus
from status_res import StatusRes
from utils import return_response, user_id_limiter
from flask_jwt_extended import jwt_required
from decorators import email_verified, check_bio_link_limit, check_subscription_expired
from extensions import db, limiter
from logger import logger

BLOG_PREFIX = "biolink"

biolink_blp = Blueprint("biolink_blp", __name__)


# create new bio link route
@biolink_blp.route(f"/{BLOG_PREFIX}/create", methods=["POST"])
@jwt_required()
@email_verified
@check_subscription_expired
@check_bio_link_limit
@limiter.limit("15 per minute", key_func=user_id_limiter)
def create_new_bio_link():
    try:
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Bio Link created successfully",
        )
    except Exception as e:
        logger.exception("error@biolink_blp/create_new_bio_link")
        logger.error(f"{e}: error@biolink_blp/create_new_bio_link")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
