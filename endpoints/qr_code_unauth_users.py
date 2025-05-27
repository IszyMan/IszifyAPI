from flask import Blueprint, request
from http_status import HttpStatus
from logger import logger
from status_res import StatusRes
from crud import (
    save_qrcode_data_unauth,
    check_unauth_url_category_exists,
)
from extensions import db
from utils import return_response
import traceback
from datetime import datetime
import pprint

QR_PREFIX = "unauth_qr_code"

unauth_qrcode_blp = Blueprint("unauth_qrcode_blp", __name__)


@unauth_qrcode_blp.route(f"/{QR_PREFIX}/qrcode", methods=["POST"])
def qrcode():
    try:
        data = request.get_json()
        user_agent = request.user_agent

        logger.info(f"Data: {data} User Agent: {user_agent}")

        category = data.get("category")
        if not category:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Category is required",
            )

        if data.get("url"):
            logger.info("checking if url exists in category")
            res = check_unauth_url_category_exists(data.get("url"), category)
            if res:
                return return_response(
                    HttpStatus.OK,
                    status=StatusRes.SUCCESS,
                    message="Data Fetched",
                    data=res.to_dict(),
                )

        payload = dict(
            url=data.get("url"),
            phone_number=data.get("phone_number"),
            message=data.get("message"),
            email=data.get("email"),
            subject=data.get("subject"),
            ssid=data.get("ssid"),
            password=data.get("password"),
            encryption=data.get("encryption"),
            ios_url=data.get("ios_url"),
            android_url=data.get("android_url"),
            other_device_url=data.get("other_device_url"),
            longitude=data.get("longitude"),
            latitude=data.get("latitude"),
            trade_number=data.get("trade_number"),
            prefix=data.get("prefix"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            company_name=data.get("company_name"),
            mobile_phone=data.get("mobile_phone"),
            fax=data.get("fax"),
            postal_code=data.get("postal_code"),
            religion=data.get("religion"),
            street=data.get("street"),
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            category=category.lower(),
            title=f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S')}",
            user_agent=str(user_agent),
        )

        qrcode_data = save_qrcode_data_unauth(payload)

        return return_response(
            HttpStatus.CREATED,
            status=StatusRes.SUCCESS,
            message="QR Code Created",
            data=qrcode_data.to_dict(),
        )

    except Exception as e:
        logger.exception("traceback@qrcode_blp/qrcode")
        logger.error(f"error@qrcode_blp/qrcode: {e}")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
