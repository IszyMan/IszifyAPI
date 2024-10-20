from flask import Blueprint, request, redirect
from http_status import HttpStatus
from status_res import StatusRes
from models import (
    current_user_info,
    Urlshort,
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
