from flask import Blueprint, redirect, request
from crud import (
    get_original_url_by_short_url,
    get_url_by_short_url,
    get_unauth_url_by_short_url,
)
import os
from utils import get_info, get_browser_info, get_computer_name
import httpagentparser
from connection.redis_connection import redis_conn

redirect_url_blp = Blueprint("redirect_url_blp", __name__)

DEFAULT_REDIRECT_URL = os.environ.get("DEFAULT_REDIRECT_URL")
FRONTEND_REDIRECT_URL = os.environ.get("FRONTEND_REDIRECT_URL")


@redirect_url_blp.route("/", methods=["GET"])
def redirect_base_url():
    return redirect(FRONTEND_REDIRECT_URL)


@redirect_url_blp.route("/<short_url>", methods=["GET"])
def redirect_url(short_url):
    from celery_config.utils.celery_works import save_clicks_for_analytics

    print(short_url, "short_url")

    user_ip = request.headers.get("x-forwarded-for", request.remote_addr)

    ip, city, country = get_info(user_ip)
    browser_name = get_browser_info(request)
    user_agent = request.headers.get("User-Agent")
    # computer_name = get_computer_name()
    computer_name = httpagentparser.detect(user_agent)["platform"]["name"]
    payload = {
        "ip_address": ip,
        "city": city,
        "country": country,
        "browser_name": browser_name,
        "device": computer_name,
    }
    print(payload, "redirect payload")

    key = f"redirect:{short_url}"
    # get from redis
    url = redis_conn.get(key)
    if not url:
        url = (
            get_url_by_short_url(short_url)
            or get_original_url_by_short_url(short_url)
            or get_unauth_url_by_short_url(short_url)
        )
        redis_conn.set(key, url, 3000)

    print(url, "url")

    save_clicks_for_analytics.delay(short_url, payload)

    # Redirect to the found URL or the default URL if not found
    return redirect(url if url else DEFAULT_REDIRECT_URL)
