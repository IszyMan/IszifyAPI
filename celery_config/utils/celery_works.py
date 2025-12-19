from celery_config.settings import celery, shared_task
from models.shorten_url import Urlshort
from models.qrcode import QRCodeData
from crud import (
    save_qrcode_clicks,
    save_url_clicks,
    save_transactions,
    save_donation,
    update_user_wallet,
)
from extensions import db
from logger import logger


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
                print(qr_url.id, "qr_url.id")
                save_qrcode_clicks(qr_url.id, payload)
                qr_url.clicks += 1
                db.session.commit()
        save_url_clicks(url.id, payload)

    print("saving url clicks +1")
    url.clicks += 1
    db.session.commit()
    print(url.url, "the real url")

    return True


# SAVE FROM VERIFY TRANSACTIONS
@shared_task
def save_transaction_from_verify_transaction(
    reference_number, amount, email, goal_id, name, message, res, user_id, trans_type
):
    try:
        save_transactions(
            user_id,
            "",
            amount,
            "",
            trans_type,
            reference_number,
            "",
            "",
            "",
            "",
            "success",
            response_json=res,
        )
        save_donation(
            goal_id, name, amount, message, True, reference_number, email, user_id
        )
        update_user_wallet(user_id, amount)
    except Exception as e:
        logger.exception(
            "traceback@celery_works/save_transaction_from_verify_transaction"
        )
        logger.error(
            f"{e}: error@celery_works/save_transaction_from_verify_transaction"
        )
        db.session.rollback()
        return False
