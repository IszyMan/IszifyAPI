from flask import Blueprint, redirect
from models import get_original_url_by_short_url, get_url_by_short_url


redirect_url_blp = Blueprint("redirect_url_blp", __name__)


@redirect_url_blp.route("/<short_url>", methods=["GET"])
def redirect_url(short_url):
    print("short_url", short_url)
    url = get_url_by_short_url(short_url)
    if not url:
        print("Checking for original url in the short url table")
        url = get_original_url_by_short_url(short_url)
    return redirect(url) if url else redirect("https://www.google.com")
