from celery_config.settings import celery, shared_task
from models.shorten_url import Urlshort
from models.qrcode import QRCodeData
from crud import save_qrcode_clicks, save_url_clicks
from extensions import db


@shared_task
def save_clicks_for_analytics(short_url, payload):
    url = Urlshort.query.filter_by(short_url=short_url).first()
    if not url:
        url = QRCodeData.query.filter_by(short_url=short_url).first()
        if not url:
            return ""
        save_qrcode_clicks(url.id, payload)
    else:
        if url.want_qr_code:
            qr_url = url.qr_code_rel
            if qr_url:
                save_qrcode_clicks(qr_url.id, payload)
                qr_url.clicks += 1
        save_url_clicks(url.id, payload)

    url.clicks += 1
    db.session.commit()
    print(url.url, "the real url")

    return True
