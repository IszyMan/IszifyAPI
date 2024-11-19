from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from models import (
    check_email_role_exist, get_one_admin,
    edit_one_admin, get_all_admins, get_all_roles,
    create_admin_account, save_role
)
from extensions import db, limiter
from utils import (
    return_response, validate_password,
    return_access_token,is_valid_email, detect_disposable_email
)
import traceback
from flask_jwt_extended import current_user, jwt_required

USER_PREFIX = "admin_account"

admin_blp = Blueprint("admin_blp", __name__)


@admin_blp.route(f"/{USER_PREFIX}/create_admin", methods=["POST"])
@jwt_required()
def create_admin():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        role_id = data.get("role_id")

        print(email, password)

        if not email or not password or not first_name or not last_name or not role_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="All fields are required",
            )

        if not is_valid_email(email):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid Email",
            )

        res = detect_disposable_email(email)
        if res == "Error" or res is None:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Network Error",
            )

        if res:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="kindly use a valid email",
            )

        if not email or not password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email and Password are required",
            )

        resp = check_email_role_exist(email, role_id)
        if resp:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message=resp,
            )

        admin_create = create_admin_account(email, password, first_name, last_name, role_id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message=f"{admin_create.last_name} {admin_create.first_name} created successfully",
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@user_blp/admin_login")
        print(e, "error@user_blp/admin_login")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# edit admin
@admin_blp.route(f"/{USER_PREFIX}/edit_admin/<admin_id>", methods=["PATCH"])
@jwt_required()
def edit_admin(admin_id):
    try:
        data = request.get_json()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        role_id = data.get("role_id")
        email = data.get("email")

        admin = get_one_admin(admin_id)
        if not admin:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Admin does not exist",
            )

        if role_id:
            resp = check_email_role_exist(email, role_id, exist_admin=admin)
            if resp:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message=resp,
                )
        edit_one_admin(admin_id, email, first_name, last_name, role_id)

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Admin updated successfully",
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@user_blp/edit_admin")
        print(e, "error@user_blp/edit_admin")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get all admins
@admin_blp.route(f"/{USER_PREFIX}/admins", methods=["GET"])
@jwt_required()
def get_admins():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        active = request.args.get("active")
        fullname = request.args.get("fullname")
        email = request.args.get("email")
        changed_password = request.args.get("changed_password")
        role_id = request.args.get("role_id")

        admins = get_all_admins(page, per_page, active, start_date,
                   end_date, fullname, email, changed_password, role_id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="All admins",
            data=[admin.to_dict() for admin in admins.items],
            page=admins.page,
            per_page=admins.per_page,
            total_items=admins.total,
            total_pages=admins.pages,
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@user_blp/get_admins")
        print(e, "error@user_blp/get_admins")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get roles
@admin_blp.route(f"/{USER_PREFIX}/roles", methods=["GET", "POST"])
@jwt_required()
def get_roles():
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
            save_role(name)
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Role Added",
            )
        roles = get_all_roles()
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="All roles",
            data=[role.to_dict() for role in roles],
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@user_blp/get_roles")
        print(e, "error@user_blp/get_roles")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get admin details
@admin_blp.route(f"/{USER_PREFIX}/admin_details", methods=["GET"])
@jwt_required()
def get_admin_details():
    try:
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Admin Details",
            data=current_user.to_dict(),
        )
    except Exception as e:
        print(traceback.format_exc(), "traceback@user_blp/get_admin_details")
        print(e, "error@user_blp/get_admin_details")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
