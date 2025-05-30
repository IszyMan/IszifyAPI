from sqlalchemy import func
from extensions import db
from models.qrcode_unauth import QRCodeDataUnauth
from utils import gen_short_code


def save_qrcode_data_unauth(qrcode_data_payload):
    qrcode_data = QRCodeDataUnauth(
        url=qrcode_data_payload["url"],
        phone_number=qrcode_data_payload["phone_number"],
        message=qrcode_data_payload["message"],
        email=qrcode_data_payload["email"],
        subject=qrcode_data_payload["subject"],
        ssid=qrcode_data_payload["ssid"],
        password=qrcode_data_payload["password"],
        encryption=qrcode_data_payload["encryption"],
        ios_url=qrcode_data_payload["ios_url"],
        android_url=qrcode_data_payload["android_url"],
        other_device_url=qrcode_data_payload["other_device_url"],
        longitude=qrcode_data_payload["longitude"],
        latitude=qrcode_data_payload["latitude"],
        trade_number=qrcode_data_payload["trade_number"],
        prefix=qrcode_data_payload["prefix"],
        first_name=qrcode_data_payload["first_name"],
        last_name=qrcode_data_payload["last_name"],
        company_name=qrcode_data_payload["company_name"],
        mobile_phone=qrcode_data_payload["mobile_phone"],
        fax=qrcode_data_payload["fax"],
        postal_code=qrcode_data_payload["postal_code"],
        religion=qrcode_data_payload["religion"],
        street=qrcode_data_payload["street"],
        city=qrcode_data_payload["city"],
        state=qrcode_data_payload["state"],
        country=qrcode_data_payload["country"],
        category=qrcode_data_payload["category"],
        short_url=gen_short_code(un_auth=True) if qrcode_data_payload["url"] else None,
        title=qrcode_data_payload.get("title"),
        user_agent=qrcode_data_payload.get("user_agent"),
    )

    db.session.add(qrcode_data)
    db.session.commit()
    return qrcode_data


def check_unauth_url_category_exists(url, category):
    return QRCodeDataUnauth.query.filter(
        func.lower(QRCodeDataUnauth.url) == url.lower(),
        func.lower(QRCodeDataUnauth.category) == category.lower(),
    ).first()


def get_unauth_url_by_short_url(short_url):
    original_url = QRCodeDataUnauth.query.filter(
        func.lower(QRCodeDataUnauth.short_url) == short_url.lower()
    ).first()
    return original_url.url if original_url else None
