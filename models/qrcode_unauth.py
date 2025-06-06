from extensions import db
from func import hex_id
from flask import request
from sqlalchemy import func
from utils import gen_short_code, return_host_url


class QRCodeDataUnauth(db.Model):
    __tablename__ = "qrcode_data_unauth"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    url = db.Column(db.Text)
    title = db.Column(db.String(150))
    phone_number = db.Column(db.String(50))
    message = db.Column(db.Text)
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
    short_url = db.Column(db.String(50))
    category = db.Column(db.String(50), nullable=False)
    user_agent = db.Column(db.Text)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<QRCodeDataUnauth: {self.category}>"

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
            "trade_number": self.trade_number,
            "prefix": self.prefix,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company_name": self.company_name,
            "mobile_phone": self.mobile_phone,
            "fax": self.fax,
            "postal_code": self.postal_code,
            "religion": self.religion,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "short_url": (
                f"{return_host_url(request.host_url)}{self.short_url}"
                if self.short_url
                else None
            ),
            "country": self.country,
            "category": self.category,
            "created": self.created.strftime("%d-%b-%Y %H:%M:%S"),
        }
        return {key: value for key, value in result.items() if value}
