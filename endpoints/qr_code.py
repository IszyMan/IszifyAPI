from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from models import (
    save_qrcode_category,
    get_qrcode_categories,
    save_qrcode_data,
    get_qrcode_data,
    update_qrcode_data,
    get_qrcode_data_by_id
)
from extensions import db, limiter
from utils import (
    return_response,
    user_id_limiter
)
import traceback
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime
import pprint

AUTH_PREFIX = "qr_code"

qrcode_blp = Blueprint("qrcode_blp", __name__)


@qrcode_blp.route(f"/{AUTH_PREFIX}/qrcode-categories", methods=["GET", "POST"])
def qrcode_categories():
    try:
        if request.method == "POST":
            data = request.get_json()
            name = data.get("name")
            if not name:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Name is required",
                )
            save_qrcode_category(name)
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="QR Code Category Added",
            )
        cats = get_qrcode_categories()
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="QR Code Categories",
            data=cats,
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@qrcode_blp/qrcode_categories")
        print(e, "error@qrcode_blp/qrcode_categories")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# create qr code
@qrcode_blp.route(f"/{AUTH_PREFIX}/qrcode", methods=["GET", "POST"])
@jwt_required()
@limiter.limit("15 per minute", key_func=user_id_limiter)
def qrcode():
    try:
        if request.method == "POST":
            data = request.get_json()

            pprint.pprint(data)

            category = data.get("category")
            social_media = data.get("social_media")
            qr_style = data.get("qr_style")
            if not category:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Category is required",
                )

            if social_media and not isinstance(social_media, list):
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Social Media must be an array",
                )

            if qr_style and not isinstance(qr_style, list):
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="QR Style must be an array",
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
                category=category,
                social_media=social_media,
                qr_style=qr_style,
            )

            save_qrcode_data(payload, current_user.id)

            return return_response(
                HttpStatus.CREATED,
                status=StatusRes.SUCCESS,
                message="QR Code Created",
            )

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        category = request.args.get("category")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        try:
            start_date = datetime.strptime(start_date, "%d-%m-%Y") if start_date else None
            end_date = datetime.strptime(end_date, "%d-%m-%Y") if end_date else None
        except ValueError as e:
            print(traceback.format_exc(), "traceback@qrcode_blp/qrcode")
            print(e, "error at date conversion")
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid date format, should be dd-mm-yyyy",
            )
        qrcodes = get_qrcode_data(
            page, per_page, current_user.id, category, start_date, end_date
        )
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="QR Codes", **qrcodes
        )

    except Exception as e:
        print(traceback.format_exc(), "traceback@qrcode_blp/qrcode")
        print(e, "error@qrcode_blp/qrcode")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# edit qr code
@qrcode_blp.route(f"/{AUTH_PREFIX}/qrcode/<qr_code_id>", methods=["GET", "PATCH"])
@jwt_required()
@limiter.limit("5 per minute", key_func=user_id_limiter)
def edit_qrcode(qr_code_id):
    try:
        if request.method == "PATCH":
            data = request.get_json()

            pprint.pprint(data)

            if not qr_code_id:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="QR Code ID is required",
                )

            social_media = data.get("social_media")
            qr_style = data.get("qr_style")
            if social_media and not isinstance(social_media, list):
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Social Media must be an array",
                )

            if qr_style and not isinstance(qr_style, list):
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="QR Style must be an array",
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
                social_media=social_media,
                qr_style=qr_style,
            )

            res = update_qrcode_data(payload, current_user.id, qr_code_id)

            if not res:
                return return_response(
                    HttpStatus.NOT_FOUND,
                    status=StatusRes.FAILED,
                    message="QR Code not found",
                )

            return return_response(
                HttpStatus.OK, status=StatusRes.SUCCESS,
                message="QR Code Updated"
            )

        # get qr code
        qr_code = get_qrcode_data_by_id(qr_code_id, current_user.id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="QR Code",
            **qr_code
        )

    except Exception as e:
        print(traceback.format_exc(), "traceback@qrcode_blp/edit_qrcode")
        print(e, "error@qrcode_blp/edit_qrcode")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
