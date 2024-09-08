from flask import Blueprint, request, redirect
from http_status import HttpStatus
from status_res import StatusRes
from models import (
    current_user_info,
    generate_short_url,
    Urlshort,
    validate_url,
    save_url_clicks,
)
from extensions import db, limiter
from utils import (
    return_response,
    get_info,
    get_computer_name,
    get_browser_info,
    user_id_limiter,
)
import traceback
from datetime import datetime
from services import send_mail
from decorators import email_verified
from flask_jwt_extended import current_user, jwt_required

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
        print(traceback.format_exc(), "traceback@user_blp/dashboard")
        print(e, "error@user_blp/dashboard")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@user_blp.route(f"{USER_PREFIX}/short_url/create", methods=["POST"])
@jwt_required()
@email_verified
@limiter.limit("5 per minute", key_func=user_id_limiter)
def shorten_url():
    try:
        print("got hereeeee")
        data = request.get_json()
        original_url = data.get("original_url")
        custom_url = data.get("custom_url")
        want_qr_code = data.get("want_qr_code", False)

        title = data.get(
            "title", f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        )

        print(
            f"original_url: {original_url}, custom_url: {custom_url}, title: {title}, "
            f"want_qr_code: {want_qr_code}"
        )

        if Urlshort.query.filter_by(user_id=current_user.id, url=original_url).first():
            return return_response(
                HttpStatus.CONFLICT,
                status=StatusRes.FAILED,
                message="URL already exists, please filter by the url to get the details",
            )
        if not validate_url(original_url):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid URL",
            )

        if custom_url:
            print(custom_url, "custom_url")
            short_url = custom_url
            if Urlshort.query.filter_by(short_url=short_url).first():
                return return_response(
                    HttpStatus.CONFLICT,
                    status=StatusRes.FAILED,
                    message="URL already exists",
                )
        else:
            short_url = generate_short_url()

        url_and_short_url = f"{request.host_url}{short_url}"

        # res = generate_and_save_qr(url_and_short_url) if generate_qr_code else ""
        # print(res, 'res')
        if want_qr_code:
            # create qr code for the short url
            pass

        url = Urlshort(
            user_id=current_user.id,
            url=original_url,
            short_url=short_url,
            title=title,
            want_qr_code=want_qr_code,
        )
        url.save()

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Short URL created successfully",
        )

    except Exception as e:
        print(traceback.format_exc(), "traceback@user_blp/shorten_url")
        print(e, "error@user_blp/shorten_url")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# redirect short url to the original url
@user_blp.route("/<short_url>/")
def redirect_to_url(short_url):
    # user_agent = request.headers.get("User-Agent")
    ip, city, country = get_info()
    browser_name = get_browser_info(request)
    computer_name = get_computer_name()
    payload = {
        "ip_address": ip,
        "city": city,
        "country": country,
        "browser_name": browser_name,
        "device": computer_name,
    }
    url = Urlshort.query.filter_by(short_url=short_url).first()
    # if not url:
    #     url = QrCode.query.filter_by(short_url=short_url).first()
    #     if not url:
    #         return ""
    # save_qrcode_clicks(url.id, payload)
    # else:
    save_url_clicks(url.id, payload)

    db.session.commit()
    print(url.url, "the real url")
    return redirect(url.url)
