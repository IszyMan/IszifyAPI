from flask import Blueprint, request
from http_status import HttpStatus
from logger import logger
from status_res import StatusRes
from crud import (
    admin_authenticate,
)
from extensions import db, limiter
from utils import (
    return_response,
    return_access_token,
)
import traceback
from flask_jwt_extended import current_user, jwt_required
from passlib.hash import pbkdf2_sha256 as hasher

USER_PREFIX = "admin_auth"

admin_auth_blp = Blueprint("admin_auth_blp", __name__)


@admin_auth_blp.route(f"/{USER_PREFIX}/login", methods=["POST"])
def admin_login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        logger.info(f"Email: {email} Password: {password}")

        if not email or not password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email and Password are required",
            )
        admin = admin_authenticate(email.lower(), password)
        if admin:
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Login Successful",
                access_token=return_access_token(admin),
            )
        return return_response(
            HttpStatus.NOT_FOUND,
            status=StatusRes.FAILED,
            message="Invalid Email or Password",
        )
    except Exception as e:
        logger.exception("traceback@user_blp/admin_login")
        logger.error(f"{e}: error@user_blp/admin_login")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
