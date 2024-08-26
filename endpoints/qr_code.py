from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from models import save_qrcode_category, get_qrcode_categories
from extensions import db
from utils import (return_response, return_access_token,
                   is_valid_email, validate_password)
import traceback
from datetime import datetime

AUTH_PREFIX = "qr_code"


qrcode_blp = Blueprint('qrcode_blp', __name__)


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
            data=cats
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
