from flask import Blueprint, request
from extensions import db
from utils import return_response
import traceback
from status_res import StatusRes
from http_status import HttpStatus
from . import pay_stack
from flask_jwt_extended import jwt_required, current_user

transactions_blp = Blueprint("transactions_blp", __name__)

TRANSACT_PREFIX = "transactions"

@transactions_blp.route(f"{TRANSACT_PREFIX}/get_banks", methods=["GET"])
def list_banks():
    try:
        res = pay_stack.get_all_banks()
        if not res:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Failed to get banks",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Banks Retrieved",
            banks=res["data"],
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@transactions_blp/list_banks")
        print(e, "error@transactions_blp/list_banks")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# verify paystack transaction

@transactions_blp.route(f"{TRANSACT_PREFIX}/verify-transaction", methods=["POST"])
# @jwt_required()
def verify_transaction():
    try:
        data = request.get_json()
        reference_number = data.get("reference")
        if not reference_number:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Reference number is required",
            )
        res = pay_stack.verify_transaction(reference_number)
        print(res, "Result of verify transaction")
        if not res:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Failed to verify transaction",
            )
        # Save the transaction to db
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Transaction Verified",
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@transactions_blp/verify_transaction")
        print(e, "error@transactions_blp/verify_transaction")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
