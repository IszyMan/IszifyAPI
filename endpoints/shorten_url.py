from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from models import (
    Urlshort,
    validate_url,
    save_want_qr_code,
    get_shorten_url_for_user,
    check_short_url_exist,
)
from extensions import db, limiter
from utils import (
    return_response,
    user_id_limiter,
    gen_short_code,
)
from logger import logger
from datetime import datetime

# from api_services import send_mail
from decorators import email_verified, check_shortlink_limit, check_subscription_expired
from flask_jwt_extended import current_user, jwt_required
from utils import get_website_title

USER_PREFIX = "url_shortener"

url_short_blp = Blueprint("url_short_blp", __name__)


@url_short_blp.route(f"{USER_PREFIX}/short_url/create", methods=["POST"])
@jwt_required()
@email_verified
@check_subscription_expired
@check_shortlink_limit
@limiter.limit("5 per minute", key_func=user_id_limiter)
def shorten_url():
    try:
        logger.info("got here")
        data = request.get_json()
        original_url = data.get("original_url")
        custom_url = data.get("custom_url")
        want_qr_code = data.get("want_qr_code", False)

        title = data.get("title")

        logger.info(
            f"original_url: {original_url}, custom_url: {custom_url}, title: {title}, "
            f"want_qr_code: {want_qr_code}"
        )

        if not original_url:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="URL you intend to shorten is required",
            )

        if not isinstance(want_qr_code, bool):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="want_qr_code must be a boolean value",
            )

        if Urlshort.query.filter_by(user_id=current_user.id, url=original_url).first():
            return return_response(
                HttpStatus.CONFLICT,
                status=StatusRes.FAILED,
                message="URL already exists, please search for the url to get the details",
            )
        # if not validate_url(original_url):
        #     return return_response(
        #         HttpStatus.BAD_REQUEST,
        #         status=StatusRes.FAILED,
        #         message="Invalid URL",
        #     )

        if custom_url:
            logger.info(f"custom_url: {custom_url}")
            short_url = custom_url
            has_half_back = True
            if Urlshort.query.filter_by(short_url=short_url).first():
                return return_response(
                    HttpStatus.CONFLICT,
                    status=StatusRes.FAILED,
                    message="You cannot use this custom url, please choose another one",
                )
        else:
            has_half_back = False
            short_url = gen_short_code(url_short=True)

        if not title:
            title = (
                get_website_title(original_url)
                or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S')}"
            )
        url = Urlshort(
            user_id=current_user.id,
            url=original_url,
            short_url=short_url,
            title=title,
            want_qr_code=want_qr_code,
            has_half_back=has_half_back,
        )
        url.save()

        if want_qr_code:
            logger.info("want_qr_code")
            save_want_qr_code(
                "url", short_url, url.id, original_url, current_user.id, title
            )

        return return_response(
            HttpStatus.CREATED,
            status=StatusRes.SUCCESS,
            message="Short URL created successfully",
        )

    except Exception as e:
        logger.exception("traceback@user_blp/shorten_url")
        logger.error(f"{e}: error@user_blp/shorten_url")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get shortened urls
@url_short_blp.route(f"{USER_PREFIX}/short_urls", methods=["GET"])
@jwt_required()
@email_verified
@limiter.limit("9 per minute", key_func=user_id_limiter)
def get_short_urls():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        hidden = bool(request.args.get("hidden", False))
        urls = get_shorten_url_for_user(page, per_page, current_user.id, hidden)
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Short URLs", **urls
        )

    except Exception as e:
        logger.exception("traceback@user_blp/get_short_urls")
        logger.error(f"{e}: error@user_blp/get_short_urls")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get one short url


@url_short_blp.route(f"{USER_PREFIX}/short_url/<short_url_id>", methods=["GET"])
@jwt_required()
@email_verified
@limiter.limit("9 per minute", key_func=user_id_limiter)
def get_one_short_url(short_url_id):
    try:
        url = Urlshort.query.filter_by(id=short_url_id, user_id=current_user.id).first()
        if not url:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="Short URL not found",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Short URL",
            data=url.to_dict(get_qr_code=True),
        )

    except Exception as e:
        logger.exception("traceback@user_blp/get_one_short_url")
        logger.error(f"{e}: error@user_blp/get_one_short_url")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# Edit shortened url


@url_short_blp.route(
    f"{USER_PREFIX}/short_url/<short_url_id>", methods=["PATCH", "DELETE"]
)
@jwt_required()
@email_verified
@limiter.limit("5 per minute", key_func=user_id_limiter)
def edit_short_url(short_url_id):
    try:
        data = request.get_json()

        if not short_url_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Short URL ID is required",
            )

        short_url = Urlshort.query.filter_by(
            id=short_url_id, user_id=current_user.id
        ).first()
        if not short_url:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="Short URL not found",
            )

        if request.method == "DELETE":
            if short_url.has_half_back or short_url.has_redirected:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="You cannot delete this short url",
                )
            short_url.delete()
            return return_response(
                HttpStatus.OK, status=StatusRes.SUCCESS, message="Short URL deleted"
            )
        title = data.get("title")
        short_link = data.get("short_link")
        hide = data.get("hide", None)

        if short_link:
            resp = check_short_url_exist(short_link)
            if resp:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="You cannot use this custom url, please choose another one",
                )

        short_url.title = title or short_url.title
        short_url.short_url = short_link or short_url.short_url
        short_url.has_half_back = True if short_link else short_url.has_half_back
        if isinstance(hide, bool):
            short_url.hidden = hide
            if short_url.want_qr_code:
                short_url.qr_code_rel.hidden = hide
        # short_url.url = url
        short_url.update()

        if short_url.want_qr_code:
            # short_url.qr_code_rel.url = url
            short_url.qr_code_rel.title = title
            short_url.qr_code_rel.update()

        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Short URL updated"
        )

    except Exception as e:
        logger.exception("traceback@user_blp/edit_short_url")
        logger.error(f"{e}: error@user_blp/edit_short_url")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# create qr code for short url
@url_short_blp.route(f"{USER_PREFIX}/create_qr_short", methods=["POST"])
@jwt_required()
@email_verified
@limiter.limit("5 per minute", key_func=user_id_limiter)
def create_qr_code():
    try:
        data = request.get_json()

        short_url_id = data.get("short_url_id")
        qr_style = data.get("qr_style", {})
        qr_frame = data.get("qr_frame", {})
        if not short_url_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Short URL ID is required",
            )
        short_url = Urlshort.query.filter_by(
            id=short_url_id, user_id=current_user.id
        ).first()
        if not short_url:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="Short URL not found",
            )

        if short_url.want_qr_code:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Short URL already has QR Code",
            )

        short_url.want_qr_code = True
        short_url.update()
        save_want_qr_code(
            "url",
            short_url.short_url,
            short_url.id,
            short_url.url,
            current_user.id,
            short_url.title,
            qr_style=qr_style,
            qr_frame=qr_frame,
        )
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="QR Code created"
        )

    except Exception as e:
        logger.exception("traceback@user_blp/create_qr_code")
        logger.error(f"{e}: error@user_blp/create_qr_code")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
