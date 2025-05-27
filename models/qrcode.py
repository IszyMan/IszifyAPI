from extensions import db
from func import hex_id
from sqlalchemy import func
from flask import request

from logger import logger
from utils import gen_short_code, return_host_url, remove_host_url
from datetime import datetime, timedelta
from default_style import return_default_style
from sqlalchemy import extract


class QRCodeCategories(db.Model):
    __tablename__ = "qrcode_categories"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100))
    display = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name.title()}

    def __init__(self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return f"<QRCodeCategory {self.name}>"


class QRCodeData(db.Model):
    __tablename__ = "qrcode_data"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    url = db.Column(db.Text)
    title = db.Column(db.String(150))
    phone_number = db.Column(db.String(50))
    message = db.Column(db.Text)
    clicks = db.Column(db.Integer, default=0)
    email = db.Column(db.String(100))
    subject = db.Column(db.String(150))
    ssid = db.Column(db.String(100))
    password = db.Column(db.String(150))
    encryption = db.Column(db.String(150))
    ios_url = db.Column(db.Text)
    android_url = db.Column(db.Text)
    other_device_url = db.Column(db.Text)
    longitude = db.Column(db.String(100))
    latitude = db.Column(db.String(100))
    trade_number = db.Column(db.String(100))
    prefix = db.Column(db.String(50))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company_name = db.Column(db.String(150))
    mobile_phone = db.Column(db.String(50))
    fax = db.Column(db.String(50))
    postal_code = db.Column(db.String(50))
    religion = db.Column(db.String(50))
    street = db.Column(db.String(150))
    city = db.Column(db.String(150))
    state = db.Column(db.String(150))
    country = db.Column(db.String(150))
    bitcoin_address = db.Column(db.String(120))
    bitcoin_amount = db.Column(db.Float)
    bitcoin_label = db.Column(db.String(100))
    bitcoin_message = db.Column(db.String(100))
    short_url = db.Column(db.String(50))
    category = db.Column(db.String(50), nullable=False)
    duplicate = db.Column(db.Boolean, default=False)
    short_url_id = db.Column(
        db.String(50), db.ForeignKey("url_shortener.id"), nullable=True
    )
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    hidden = db.Column(db.Boolean, default=False)
    social_media = db.relationship(
        "SocialMedia", backref="qrcode", lazy=True, cascade="all, delete"
    )
    qr_style = db.relationship(
        "QrCodeStyling",
        backref="qrcode",
        lazy=True,
        uselist=False,
        cascade="all, delete",
    )
    qr_frame = db.relationship(
        "QrFrame",
        backref="qrcode",
        lazy=True,
        uselist=False,
        cascade="all, delete",
    )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<QRCodeData {self.category}>"

    def to_dict(self):
        result = {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "phone_number": self.phone_number,
            "message": self.message,
            "email": self.email,
            "subject": self.subject,
            "ssid": self.ssid,
            "password": self.password,
            "encryption": self.encryption,
            "ios_url": self.ios_url,
            "android_url": self.android_url,
            "other_device_url": self.other_device_url,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "short_url_id": self.short_url_id or None,
            "trade_number": self.trade_number,
            "prefix": self.prefix,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "hidden": self.hidden,
            "company_name": self.company_name,
            "mobile_phone": self.mobile_phone,
            "fax": self.fax,
            "postal_code": self.postal_code,
            "religion": self.religion,
            "street": self.street,
            "city": self.city,
            "bitcoin_address": self.bitcoin_address,
            "bitcoin_amount": self.bitcoin_amount,
            "bitcoin_label": self.bitcoin_label,
            "bitcoin_message": self.bitcoin_message,
            "state": self.state,
            "duplicate": self.duplicate or False,
            "host_url": remove_host_url(request.host_url),
            "short_link": self.short_url or None,
            "short_url": (
                f"{return_host_url(request.host_url)}{self.short_url}"
                if self.short_url
                else None
            ),
            "country": self.country,
            "category": self.category,
            "created": self.created.strftime("%d-%b-%Y %H:%M:%S"),
            "social_media": (
                [sm.to_dict() for sm in self.social_media] if self.social_media else []
            ),
            "qr_style": (
                self.qr_style.to_dict() if self.qr_style else return_default_style()
            ),
            "qr_frame": self.qr_frame.to_dict() if self.qr_frame else {},
        }
        return {
            key: value
            for key, value in result.items()
            if value or key in ["duplicate", "hidden"]
        }


class QrFrame(db.Model):
    __tablename__ = "qr_frame"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    frame = db.Column(db.Text, nullable=False)
    scan_name = db.Column(db.String(100), nullable=False)
    qrcode_id = db.Column(db.String(50), db.ForeignKey("qrcode_data.id"))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<QrFrame {self.scan_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "frame": self.frame,
            "scan_name": self.scan_name,
        }


class QrCodeStyling(db.Model):
    __tablename__ = "qr_code_styling"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    qrcode_id = db.Column(db.String(50), db.ForeignKey("qrcode_data.id"))

    width = db.Column(db.Integer, default=200)
    height = db.Column(db.Integer, default=200)
    image = db.Column(db.Text, nullable=True)
    margin = db.Column(db.Integer, default=0)

    qr_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for QR options
    image_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for image options
    dots_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for dots options
    background_options = db.Column(
        db.JSON, nullable=False
    )  # Dynamic JSON for background options
    corners_square_options = db.Column(
        db.JSON, nullable=False
    )  # Dynamic JSON for square corners options
    corners_dot_options = db.Column(
        db.JSON, nullable=False
    )  # Dynamic JSON for dot corners options
    frame_text = db.Column(db.Text, nullable=True)
    frame_color = db.Column(db.String(100), nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        data_to_return = {
            "id": self.id,
            "width": self.width,
            "height": self.height,
            "image": self.image,
            "margin": self.margin,
            "qrOptions": self.qr_options,
            "imageOptions": self.image_options,
            "dotsOptions": self.dots_options,
            "backgroundOptions": self.background_options,
            "cornersSquareOptions": self.corners_square_options,
            "cornersDotOptions": self.corners_dot_options,
            "frame_text": self.frame_text,
            "frame_color": self.frame_color,
        }
        return {key: value for key, value in data_to_return.items() if value}


class SocialMedia(db.Model):
    __tablename__ = "social_media"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=False)
    qrcode_id = db.Column(db.String(50), db.ForeignKey("qrcode_data.id"))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return {"id": self.id, "name": self.name, "url": self.url}


class QrcodeRecord(db.Model):
    __tablename__ = "qr_code_record"
    __table_args__ = (
        db.Index('idx_qr_code_record_qr_code_id', 'qr_code_id'),  # Added index for faster queries
    )

    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    qr_code_id = db.Column(
        db.String(50),
        db.ForeignKey("qrcode_data.id", ondelete='CASCADE'),  # Added cascade
        nullable=False,  # Explicitly marked as non-nullable
        index=True  # Index for faster joins
    )
    date = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.now()  # Added server default
    )
    clicks = db.Column(
        db.Integer,
        default=0,
        nullable=False,  # Explicitly marked as non-nullable
    )


class QrCodeClickLocation(db.Model):
    __tablename__ = "qr_code_click_location"
    __table_args__ = (
        db.Index('idx_qr_code_click_location_qr_code_id', 'qr_code_id'),  # Added index
        db.Index('idx_qr_code_click_location_created', 'created'),  # Added index for time-based queries
    )

    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    ip_address = db.Column(db.String(39))  # Reduced length for IPv6
    country = db.Column(db.String(56))  # ISO country code max length
    city = db.Column(db.String(100))  # Reduced length
    device = db.Column(db.String(50))  # Reduced length
    browser = db.Column(db.String(50))  # Reduced length
    qr_code_id = db.Column(
        db.String(50),
        db.ForeignKey("qrcode_data.id", ondelete='CASCADE'),  # Added cascade
        nullable=False,  # Explicitly marked as non-nullable
        index=True  # Index for faster joins
    )
    created = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
        server_default=db.func.now()  # Added server default
    )
