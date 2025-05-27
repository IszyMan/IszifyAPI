from flask import Blueprint, request, redirect
from http_status import HttpStatus
from status_res import StatusRes
from crud import (
    current_user_info,
    save_url_clicks,
    get_user_current_subscription,
    get_users_subscriptions,
)
from models.shorten_url import Urlshort
from extensions import db, limiter
from utils import (
    return_response,
    get_info,
    get_computer_name,
    get_browser_info,
    user_id_limiter,
    validate_password,
)
from logger import logger
from decorators import email_verified
from flask_jwt_extended import current_user, jwt_required
from passlib.hash import pbkdf2_sha256 as hasher

USER_PREFIX = "user"

user_blp = Blueprint("user_blp", __name__)


@user_blp.route(f"/{USER_PREFIX}/dashboard", methods=["GET"])
@jwt_required()
@email_verified
@limiter.limit("5 per minute", key_func=user_id_limiter)
def dashboard():
    try:
        res = current_user_info(current_user)
        return return_response(
            HttpStatus.OK, message="User Dashboard", status=StatusRes.SUCCESS, data=res
        )
    except Exception as e:
        logger.exception("traceback@user_blp/dashboard")
        logger.error(f"{e}: error@user_blp/dashboard")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# redirect short url to the original url
# @user_blp.route("/<short_url>/")
# def redirect_to_url(short_url):
#     # user_agent = request.headers.get("User-Agent")
#     ip, city, country = get_info()
#     browser_name = get_browser_info(request)
#     computer_name = get_computer_name()
#     payload = {
#         "ip_address": ip,
#         "city": city,
#         "country": country,
#         "browser_name": browser_name,
#         "device": computer_name,
#     }
#     url = Urlshort.query.filter_by(short_url=short_url).first()
#     # if not url:
#     #     url = QrCode.query.filter_by(short_url=short_url).first()
#     #     if not url:
#     #         return ""
#     # save_qrcode_clicks(url.id, payload)
#     # else:
#     save_url_clicks(url.id, payload)
#
#     db.session.commit()
#     return redirect(url.url)


# user settings
# @user_blp.route(f"/{USER_PREFIX}/settings", methods=["PATCH"])
# @jwt_required()
# @email_verified
# @limiter.limit("5 per minute", key_func=user_id_limiter)
# def settings():
#     try:
#         data = request.get_json()
#         current_user.first_name = data.get("first_name", current_user.first_name)
#         current_user.last_name = data.get("last_name", current_user.last_name)
#         current_user.update()
#         return return_response(
#             HttpStatus.OK, message="User Settings", status=StatusRes.SUCCESS
#         )
#     except Exception as e:
#         logger.exception( "traceback@user_blp/settings")
#         logger.error(f"{e}: error@user_blp/settings")
#         db.session.rollback()
#         return return_response(
#             HttpStatus.INTERNAL_SERVER_ERROR,
#             status=StatusRes.FAILED,
#             message="Network Error",
#         )
# change password
@user_blp.route(f"/{USER_PREFIX}/change-password", methods=["PATCH"])
@jwt_required()
@email_verified
@limiter.limit("5 per minute", key_func=user_id_limiter)
def change_password():
    try:
        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        if not old_password or not new_password or not confirm_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="All fields are required",
            )

        if not hasher.verify(old_password, current_user.password):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Old password is incorrect",
            )

        pass_valid_msg = validate_password(new_password)

        if pass_valid_msg:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message=pass_valid_msg,
            )

        if new_password != confirm_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Passwords do not match",
            )

        current_user.password = hasher.hash(new_password)
        current_user.update()

        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Password changed"
        )
    except Exception as e:
        logger.exception("traceback@user_blp/settings")
        logger.error(f"{e}: error@user_blp/settings")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# user details
@user_blp.route(f"/{USER_PREFIX}/details", methods=["GET"])
@jwt_required()
def get_user_details():
    try:
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="User Details",
            data=current_user.to_dict(),
        )
    except Exception as e:
        logger.exception("traceback@user_blp/get_user_details")
        logger.error(f"{e}: error@user_blp/get_user_details")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get user current sub
@user_blp.route(f"/{USER_PREFIX}/sub", methods=["GET"])
@jwt_required()
def get_user_sub():
    try:
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="User Subscription",
            data=get_user_current_subscription(current_user),
        )
    except Exception as e:
        logger.exception("traceback@user_blp/get_user_sub")
        logger.error(f"{e}: error@user_blp/get_user_sub")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get all user subs
@user_blp.route(f"/{USER_PREFIX}/all-sub", methods=["GET"])
@jwt_required()
def get_user_subs():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="User Subscriptions",
            **get_users_subscriptions(page, per_page, current_user),
        )
    except Exception as e:
        logger.exception("traceback@user_blp/get_user_subs")
        logger.error(f"{e}: error@user_blp/get_user_subs")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
