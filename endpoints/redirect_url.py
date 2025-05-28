from flask import Blueprint, redirect, request
from crud import (
    get_original_url_by_short_url,
    get_url_by_short_url,
    get_unauth_url_by_short_url,
)
import os
from utils import get_info, get_browser_info, get_computer_name

redirect_url_blp = Blueprint("redirect_url_blp", __name__)

DEFAULT_REDIRECT_URL = os.environ.get("DEFAULT_REDIRECT_URL")


@redirect_url_blp.route("/<short_url>", methods=["GET"])
def redirect_url(short_url):
    from celery_config.utils.celery_works import save_clicks_for_analytics

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
    url = (
        get_url_by_short_url(short_url)
        or get_original_url_by_short_url(short_url)
        or get_unauth_url_by_short_url(short_url)
    )

    save_clicks_for_analytics.delay(short_url, payload)

    # Redirect to the found URL or the default URL if not found
    return redirect(url if url else DEFAULT_REDIRECT_URL)
