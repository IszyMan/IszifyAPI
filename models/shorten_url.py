import datetime
import hashlib
import uuid

# from main import create_app
from urllib import request
from urllib.error import HTTPError, URLError

from hashids import Hashids
from sqlalchemy import extract, func

from extensions import db
from func import hex_id
from decorators import retry_on_exception
from utils import return_host_url
from flask import request

# from sqlalchemy.dialects.postgresql import BYTEA

secret = "any-secret-key-you-choose"

hashids = Hashids(min_length=6, salt=secret)


# url shortener table
class Urlshort(db.Model):
    __tablename__ = "url_shortener"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    url = db.Column(db.Text)
    short_url = db.Column(db.String(250))
    title = db.Column(db.String(250))
    want_qr_code = db.Column(db.Boolean, default=False)
    # relationship to qr code
    qr_code_rel = db.relationship("QRCodeData", backref="url_shortener", uselist=False, cascade="all, delete")
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Urlshort('{self.url}', '{self.short_url}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "short_url": f"{return_host_url(request.host_url)}{self.short_url}",
            "title": self.title,
            "want_qr_code": self.want_qr_code,
            "created": self.created
        }


# clicks model
class UrlShortenerClicks(db.Model):
    __tablename__ = "url_shortener_clicks"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    count = db.Column(db.Integer, default=0)
    url_id = db.Column(db.String(50), db.ForeignKey("url_shortener.id"))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Clicks('{self.url_id}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class ShortUrlClickLocation(db.Model):
    __tablename__ = "short_url_click_location"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    ip_address = db.Column(db.String(250))
    country = db.Column(db.String(250))
    city = db.Column(db.String(250))
    device = db.Column(db.String(250))
    browser = db.Column(db.String(250))
    url_id = db.Column(db.String(50), db.ForeignKey("url_shortener.id"))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Clicks('{self.url_id}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


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
        print("save new click record")
        new_clicks = UrlShortenerClicks(count=1, url_id=url_id)
        db.session.add(new_clicks)
    else:
        print("update click record")
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


@retry_on_exception(retries=3, delay=1)
def get_original_url_by_short_url(short_url):
    origin_url = Urlshort.query.filter(
        func.lower(Urlshort.short_url) == short_url.lower()
    ).first()
    return origin_url.url if origin_url else None


def save_shorten_url(url, short_url, title, want_qr_code, user_id):
    new_record = Urlshort(
        url=url, short_url=short_url, title=title, want_qr_code=want_qr_code,
        user_id=user_id
    )
    db.session.add(new_record)
    db.session.commit()
    return new_record


def get_shorten_url_for_user(page, per_page, user_id):
    query = Urlshort.query.filter_by(user_id=user_id)

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
