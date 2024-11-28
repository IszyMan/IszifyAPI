from flask import Blueprint
from extensions import db
from utils import return_response
import traceback
from status_res import StatusRes
from http_status import HttpStatus

transactions_blp = Blueprint("transactions_blp", __name__)

@transactions_blp.route("/get_banks", methods=["GET"])
def list_banks():
    try:
        pass
    except Exception as e:
        print(traceback.format_exc(), "traceback@transactions_blp/list_banks")
        print(e, "error@transactions_blp/list_banks")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Failed to get banks",
        )
