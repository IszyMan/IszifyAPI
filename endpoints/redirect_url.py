from flask import Blueprint, redirect
from models import get_original_url_by_short_url, get_url_by_short_url


redirect_url_blp = Blueprint("redirect_url_blp", __name__)

DEFAULT_REDIRECT_URL = "https://www.google.com"


@redirect_url_blp.route("/<short_url>", methods=["GET"])
def redirect_url(short_url):
    print("redirect_url")
    url = get_url_by_short_url(short_url) or get_original_url_by_short_url(short_url)

    # Redirect to the found URL or the default URL if not found
    return redirect(url if url else DEFAULT_REDIRECT_URL)
