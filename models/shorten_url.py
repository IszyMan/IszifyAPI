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
from logger import logger
from utils import return_host_url, remove_host_url
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
    clicks = db.Column(db.Integer, default=0)
    want_qr_code = db.Column(db.Boolean, default=False)
    has_half_back = db.Column(db.Boolean, default=False)
    has_redirected = db.Column(db.Boolean, default=False)
    hidden = db.Column(db.Boolean, default=False)
    # relationship to qr code
    qr_code_rel = db.relationship(
        "QRCodeData", backref="url_shortener", uselist=False, cascade="all, delete"
    )
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    # the clicks
    url_shortener_clicks = db.relationship(
        "UrlShortenerClicks", backref="url_shortener", cascade="all, delete"
    )

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

    def to_dict(self, get_qr_code=False):
        sh_dic = {
            "id": self.id,
            "url": self.url,
            "short_url": f"{return_host_url(request.host_url)}{self.short_url}",
            "short_link": self.short_url,
            "host_url": remove_host_url(request.host_url),
            "title": self.title,
            "want_qr_code": self.want_qr_code,
            "created": self.created.strftime("%d-%b-%Y %H:%M:%S"),
            "has_half_back": self.has_half_back or False,
            "has_redirected": self.has_redirected or False,
            "hidden": self.hidden or False,
            "active": not self.hidden,
        }

        if get_qr_code and self.qr_code_rel:
            sh_dic["qr_code"] = self.qr_code_rel.to_dict()
        return sh_dic


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

    def to_dict_urlshort(self):
        return {
            "id": self.id,
            "count": self.count,
            "long_url": self.url_shortener.url,
            "short_url": f"{return_host_url(request.host_url)}{self.url_shortener.short_url}",
            "title": self.url_shortener.title,
        }


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

    def to_dict(self, city=False, country=False, device=False, browser=False):
        pre_dict = {
            "id": self.id,
        }
        if city:
            pre_dict["city"] = self.city
        if country:
            pre_dict["country"] = self.country
        if device:
            pre_dict["device"] = self.device
        if browser:
            pre_dict["browser"] = self.browser
        return pre_dict
