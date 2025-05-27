from urllib import request
from urllib.error import HTTPError, URLError
import uuid
import hashlib
import datetime
from extensions import db
from func import hex_id
from sqlalchemy import func
from sqlalchemy import extract
from logger import logger
from models.shorten_url import UrlShortenerClicks, ShortUrlClickLocation, Urlshort


def save_url_clicks(url_id, payload):
    # Get today's date components
    today = datetime.datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # Query to find today's clicks for the given url_id
    clicks = UrlShortenerClicks.query.filter(
        UrlShortenerClicks.url_id == url_id,
        extract("year", UrlShortenerClicks.created) == current_year,
        extract("month", UrlShortenerClicks.created) == current_month,
        extract("day", UrlShortenerClicks.created) == current_day,
    ).first()

    if not clicks:
        logger.info("save new click record")
        new_clicks = UrlShortenerClicks(count=1, url_id=url_id)
        db.session.add(new_clicks)
    else:
        logger.info("update click record")
        clicks.count += 1

    db.session.commit()
    save_url_click_location(
        payload["ip_address"],
        payload["country"],
        payload["city"],
        payload["device"],
        payload["browser_name"],
        url_id,
    )
    return True


# generate short url
def generate_short_url():
    last_url = Urlshort.query.order_by(Urlshort.id.desc()).first()

    if not last_url:
        # If no URLs exist in the database, initialize the counter to 1
        new_uuid = uuid.uuid4().hex
    else:
        # Use the last UUID if it exists
        new_uuid = last_url.id

    # Generate the short URL using the counter
    hashid = hashlib.sha256(new_uuid.encode()).hexdigest()[:8]
    return hashid


# validate url
def validate_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    try:
        request.urlopen(url)
        return True
    except (HTTPError, URLError):
        return False


def save_url_click_location(ip_address, country, city, device, browser, url_id):
    new_record = ShortUrlClickLocation(
        ip_address=ip_address,
        country=country,
        city=city,
        device=device,
        browser=browser,
        url_id=url_id,
    )
    db.session.add(new_record)
    db.session.commit()
    return True


def get_original_url_by_short_url(short_url):
    origin_url = Urlshort.query.filter(
        func.lower(Urlshort.short_url) == short_url.lower()
    ).first()
    return origin_url.url if origin_url else None


def save_shorten_url(url, short_url, title, want_qr_code, user_id):
    new_record = Urlshort(
        url=url,
        short_url=short_url,
        title=title,
        want_qr_code=want_qr_code,
        user_id=user_id,
    )
    db.session.add(new_record)
    db.session.commit()
    return new_record


def get_shorten_url_for_user(page, per_page, user_id, hidden):
    query = Urlshort.query.filter_by(user_id=user_id, hidden=hidden)

    # Order by creation date descending and paginate
    shorten_urls = query.order_by(Urlshort.created.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        "data": [shorten_url.to_dict() for shorten_url in shorten_urls.items],
        "total_items": shorten_urls.total,
        "page": shorten_urls.page,
        "total_pages": shorten_urls.pages,
        "per_page": shorten_urls.per_page,
    }


def check_short_url_exist(short_url):
    return Urlshort.query.filter(Urlshort.short_url == short_url).first()


def get_current_shortlink_count(current_user):
    """Return the current count of Urlshort records."""
    now = datetime.datetime.utcnow()
    return (
        Urlshort.query.filter_by(user=current_user)
        .filter(extract("year", Urlshort.created) == now.year)
        .filter(extract("month", Urlshort.created) == now.month)
        .count()
    )
