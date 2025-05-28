from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from crud import (
    authenticate,
    create_user,
    get_user,
    create_reset_p,
    get_user_by_reset_p,
    change_password,
    create_otp,
    username_exist,
    email_exist,
    subscribe_for_beginner,
)
from extensions import db, limiter
from utils import (
    return_response,
    return_access_token,
    is_valid_email,
    validate_password,
    detect_disposable_email,
)
from datetime import datetime
from api_services import send_mail, send_html_email
from passlib.hash import pbkdf2_sha256 as hasher
from logger import logger


AUTH_PREFIX = "auth"


auth_blp = Blueprint("auth_blp", __name__)


@auth_blp.route(f"/{AUTH_PREFIX}/login", methods=["POST"])
@limiter.limit("3 per minute")
def login():
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
        user = authenticate(email.lower(), password)
        if user:
            if not user.email_verified:
                return return_response(
                    HttpStatus.FORBIDDEN,
                    status=StatusRes.FAILED,
                    message="Email not verified",
                    email_verified=user.email_verified,
                )
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Login Successful",
                access_token=return_access_token(user),
                email_verified=user.email_verified,
            )
        return return_response(
            HttpStatus.NOT_FOUND,
            status=StatusRes.FAILED,
            message="Invalid Email or Password",
        )
    except Exception as e:
        logger.exception("traceback@auth_blp/login")
        logger.error(f"{e}: error@auth_blp/login")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@auth_blp.route(f"/{AUTH_PREFIX}/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not email or not password or not first_name or not last_name or not username:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="All fields are required",
            )

        if not is_valid_email(email):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid Email",
            )

        res = detect_disposable_email(email)
        if res == "Error" or res is None:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Network Error",
            )
        if res:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Disposable Email not allowed",
            )

        if username_exist(username.lower()):
            return return_response(
                HttpStatus.CONFLICT,
                status=StatusRes.FAILED,
                message="Username already exists",
            )

        if email_exist(email.lower()):
            return return_response(
                HttpStatus.CONFLICT,
                status=StatusRes.FAILED,
                message="Email already exists",
            )

        pass_valid_msg = validate_password(password)

        if pass_valid_msg:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message=pass_valid_msg,
            )

        user, message = create_user(email, password, first_name, last_name, username)

        if message:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message=message,
            )

        otp = user.user_session.otp
        logger.info(f"OTP: {otp}")
        # implement where to send the user an otp after registration
        # email_payload = {
        #     "otp": otp,
        #     "email": user.email,
        #     "subject": "Verify your account",
        #     "template_name": "otp.html",
        # }
        # send_mail(email_payload)

        send_html_email(
            recipients=[
                {"email": user.email, "name": f"{user.last_name} {user.first_name}"}
            ],
            subject="Verify your account",
            template_path="otp.html",
            template_context={"otp": otp},
        )

        return return_response(
            HttpStatus.CREATED,
            status=StatusRes.SUCCESS,
            message="An email has been sent to verify your account",
            user_email=user.email,
        )

    except Exception as e:
        logger.exception("traceback@auth_blp/register")
        logger.error(f"{e}: error@auth_blp/register")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# resend otp
@auth_blp.route(f"/{AUTH_PREFIX}/resend-otp", methods=["POST"])
def resend_otp():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required",
            )

        user = get_user(email)

        if not user:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="User not found",
            )

        if user.email_verified:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email already verified",
            )

        user_session = create_otp(user.id)

        otp = user_session.otp
        logger.info(f"OTP: {otp}")
        # implement where to send the user an otp
        # email_payload = {
        #     "otp": otp,
        #     "email": user.email,
        #     "subject": "(Otp Resend)-Verify your account",
        #     "template_name": "otp.html",
        # }
        # send_mail(email_payload)

        send_html_email(
            recipients=[
                {"email": user.email, "name": f"{user.last_name} {user.first_name}"}
            ],
            subject="(Otp Resend)-Verify your account",
            template_path="otp.html",
            template_context={"otp": otp},
        )

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="An email has been sent to verify your account",
            user_email=user.email,
        )

    except Exception as e:
        logger.exception("traceback@auth_blp/resend-otp")
        logger.error(f"{e}: error@auth_blp/resend-otp")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# verify email
@auth_blp.route(f"/{AUTH_PREFIX}/verify-account", methods=["PATCH"])
def verify_account():
    try:
        data = request.get_json()
        otp = data.get("otp")
        email = data.get("email")

        if not otp:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="OTP is required",
            )

        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required",
            )

        user = get_user(email)

        if not user:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="User not found",
            )

        if user.email_verified:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email already verified",
            )

        if user.user_session.otp != otp:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid OTP",
            )

        if user.user_session.otp_expiry < datetime.now():
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="OTP expired",
            )

        user.email_verified = True
        subscribe_for_beginner(user.id)
        db.session.commit()

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Email verified successfully",
            access_token=return_access_token(user),
        )

    except Exception as e:
        logger.exception("traceback@auth_blp/verify-account")
        logger.error(f"{e}: error@auth_blp/verify-account")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# forgotten password
@auth_blp.route(f"/{AUTH_PREFIX}/forgot-password-request", methods=["PATCH"])
def forgot_password_request():
    try:
        data = request.get_json()

        email = data.get("email")
        frontend_url = data.get("frontend_url")

        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required",
            )

        if not frontend_url:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Frontend URL is required",
            )

        user = get_user(email)

        if not user:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="User not found",
            )

        user_reset = create_reset_p(user.id)

        logger.info(f"Frontend URL: {frontend_url}")

        frontend_url = (
            f"http://{frontend_url}"
            if not frontend_url.startswith("http")
            else frontend_url
        )
        reset_link = f"{frontend_url}/{user_reset.reset_p}"
        logger.info(f"Reset Link: {reset_link}")
        # send this reset link to the user

        # email_payload = {
        #     "reset_link": reset_link,
        #     "email": user.email,
        #     "subject": "Reset your password",
        #     "template_name": "reset_password.html",
        # }
        # send_mail(email_payload)

        send_html_email(
            recipients=[
                {"email": user.email, "name": f"{user.last_name} {user.first_name}"}
            ],
            subject="Reset your password",
            template_path="reset_password.html",
            template_context={"reset_link": reset_link},
        )

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Password reset request sent successfully",
            user_email=user.email,
        )

    except Exception as e:
        logger.exception("traceback@auth_blp/forgot-password-request")
        logger.error(f"{e}: error@auth_blp/forgot-password-request")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# reset password
@auth_blp.route(f"/{AUTH_PREFIX}/reset-password/<reset_p>", methods=["PATCH"])
def reset_password(reset_p):
    try:
        data = request.get_json()

        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if not reset_p:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Reset password token is required",
            )

        user = get_user_by_reset_p(reset_p)

        if not user:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="User not found",
            )

        if user.user_session.reset_p_invalid:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Revoked token",
            )

        # if the reset password token has expired
        if user.user_session.reset_p_expiry < datetime.now():
            user.user_session.reset_p_invalid = True
            db.session.commit()
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Reset password token has expired",
            )

        if reset_p and (not confirm_password and not new_password):
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Please provide old and new password",
            )

        if not confirm_password and new_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Confirm password is required",
            )

        if confirm_password and not new_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="New password is required",
            )

        if new_password != confirm_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Passwords do not match",
            )

        # check if the new password is the same as the old password
        if hasher.verify(new_password, user.password):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="New password cannot be the same as the old password",
            )

        pass_change = change_password(user, new_password)

        if pass_change:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message=pass_change,
            )

        user.user_session.reset_p_invalid = True
        db.session.commit()

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Password reset successfully",
        )

    except Exception as e:
        logger.exception("traceback@auth_blp/reset-password")
        logger.error(f"{e}: error@auth_blp/reset-password")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
