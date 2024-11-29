from flask import Blueprint
from extensions import db
from utils import return_response
import traceback
from status_res import StatusRes
from http_status import HttpStatus
from . import pay_stack

transactions_blp = Blueprint("transactions_blp", __name__)

TRANSACT_PREFIX = "transactions"

@transactions_blp.route(f"{TRANSACT_PREFIX}/get_banks", methods=["GET"])
def list_banks():
    try:
        res = pay_stack.get_banks()
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
            data=res
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@transactions_blp/list_banks")
        print(e, "error@transactions_blp/list_banks")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Failed to get banks",
        )
