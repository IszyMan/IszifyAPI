from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from utils import return_response, user_id_limiter, get_website_title
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime
import pprint
from decorators import email_verified
from extensions import db, limiter
import traceback

BLOG_PREFIX = "biolink"

biolink_blp = Blueprint("biolink_blp", __name__)

# create new bio link route
@biolink_blp.route(f"/{BLOG_PREFIX}/create", methods=["POST"])
@jwt_required()
@email_verified
@limiter.limit("15 per minute", key_func=user_id_limiter)
def create_new_bio_link():
    try:
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Bio Link created successfully"
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@biolink_blp/create_new_bio_link")
        print(e, "error@biolink_blp/create_new_bio_link")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
