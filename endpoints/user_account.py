from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from models import current_user_info
from extensions import db
from utils import return_response
import traceback
from datetime import datetime
from services import send_mail
from flask_jwt_extended import current_user, jwt_required

USER_PREFIX = "user"


user_blp = Blueprint('user_blp', __name__)


@user_blp.route(f"/{USER_PREFIX}/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    try:
        res = current_user_info(current_user)
        return return_response(HttpStatus.OK,
                               message="User Dashboard",
                               status=StatusRes.SUCCESS, data=res)
    except Exception as e:
        print(traceback.format_exc(), "traceback@user_blp/dashboard")
        print(e, "error@user_blp/dashboard")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
