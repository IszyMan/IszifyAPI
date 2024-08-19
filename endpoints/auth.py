from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from models import authenticate, create_user, get_user
from extensions import db
from utils import return_response, return_access_token, is_valid_email, validate_password
import traceback

AUTH_PREFIX = "auth"


auth = Blueprint('auth', __name__)


@auth.route(f"/{AUTH_PREFIX}/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        print(email, password)

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
                )
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Login Successful",
                access_token=return_access_token(user),
            )
        return return_response(
            HttpStatus.NOT_FOUND,
            status=StatusRes.FAILED,
            message="Invalid Email or Password",
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@auth/login")
        print(e, "error@auth/login")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@auth.route(f"/{AUTH_PREFIX}/register", methods=["POST"])
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

        otp = user.otp
        print(otp, "OTP")
        # implement where to send the user an otp after registration

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="An email has been sent to verify your account",
            user_email=user.email
        )

    except Exception as e:
        print(traceback.format_exc(), "traceback@auth/register")
        print(e, "error@auth/register")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# resend otp
@auth.route(f"/{AUTH_PREFIX}/resend-otp", methods=["POST"])
def resend_otp():
    pass


# verify email
@auth.route(f"/{AUTH_PREFIX}/verify-account", methods=["PATCH"])
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

        if not user.email_verified:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email already verified",
            )

        if user.otp != otp:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid OTP",
            )

        user.email_verified = True
        db.session.commit()

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Email verified successfully",
        )

    except Exception as e:
        print(traceback.format_exc(), "traceback@auth/verify-account")
        print(e, "error@auth/verify-account")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# forgotten password
@auth.route(f"/{AUTH_PREFIX}/forgot-password", methods=["POST"])
def forgot_password():
    pass
