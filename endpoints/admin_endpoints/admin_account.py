from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from crud import (
    check_email_role_exist,
    get_one_admin,
    edit_one_admin,
    get_all_admins,
    get_all_roles,
    create_admin_account,
    save_role,
    create_payment_plan,
    get_payment_plans,
    edit_payment_plan,
    delete_payment_plan,
    get_one_role,
    delete_one_admin
)
from extensions import db, limiter
from utils import (
    return_response,
    validate_password,
    return_access_token,
    is_valid_email,
    detect_disposable_email,
)
from logger import logger
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

        logger.info(f"email: {email}, password: {password}")

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

        admin_create = create_admin_account(
            email, password, first_name, last_name, role_id
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message=f"{admin_create.last_name} {admin_create.first_name} created successfully",
        )
    except Exception as e:
        logger.exception("traceback@user_blp/admin_login")
        logger.error(f"{e}: error@user_blp/admin_login")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# edit admin
@admin_blp.route(f"/{USER_PREFIX}/edit_admin/<admin_id>", methods=["PATCH", "DELETE"])
@jwt_required()
def edit_admin(admin_id):
    try:
        admin = get_one_admin(admin_id)
        if not admin:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Admin does not exist",
            )

        if request.method == "PATCH":
            data = request.get_json()
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            role_id = data.get("role_id")
            email = data.get("email")

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
        elif request.method == "DELETE":
            delete_one_admin(admin_id)
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Admin deleted successfully",
            )
    except Exception as e:
        logger.exception("traceback@user_blp/edit_admin")
        logger.error(f"{e}: error@user_blp/edit_admin")
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

        admins = get_all_admins(
            page,
            per_page,
            active,
            start_date,
            end_date,
            fullname,
            email,
            changed_password,
            role_id,
        )
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
        logger.exception("traceback@user_blp/get_admins")
        logger.error(f"{e}: error@user_blp/get_admins")
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
        logger.exception("traceback@user_blp/get_roles")
        logger.error(f"{e}: error@user_blp/get_roles")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# edit and delete role
@admin_blp.route(f"/{USER_PREFIX}/role/<role_id>", methods=["PATCH", "DELETE"])
@jwt_required()
def role_operation(role_id):
    try:
        role = get_one_role(role_id)
        if not role:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Role does not exist",
            )
        
        if request.method == "DELETE":
            role.delete()
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Role Deleted",
            )
        elif request.method == "PATCH":
            data = request.get_json()
            name = data.get("name", role.name)
            role.name = name
            role.update()
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Role Updated",
            )
        else:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid Request Method",
            )
    except Exception as e:
        logger.exception("traceback@user_blp/role_operation")
        logger.error(f"{e}: error@user_blp/role_operation")
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
        logger.exception("traceback@user_blp/get_admin_details")
        logger.error(f"{e}: error@user_blp/get_admin_details")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# add payment plan
@admin_blp.route(f"/{USER_PREFIX}/payment_plan", methods=["GET", "POST"])
@jwt_required()
def add_payment_plan():
    try:
        if request.method == "GET":
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Payment Plan Retrieved",
                plans=get_payment_plans(),
            )
        data = request.get_json()
        name = data.get("name")
        amount = float(data.get("amount"))
        currency = data.get("currency")
        duration = int(data.get("duration", 1))
        unlimited_link_clicks = bool(data.get("unlimited_link_clicks", False))
        unlimited_qr_scans = bool(data.get("unlimited_qr_scans", False))
        shortlinks_per_month = int(data.get("shortlinks_per_month", 0))
        qr_codes_per_month = int(data.get("qr_codes_per_month", 0))
        link_in_bio = int(data.get("link_in_bio", 0))
        analytics_access = bool(data.get("analytics_access", False))
        qr_code_customization = bool(data.get("qr_code_customization", False))
        qr_code_watermark = bool(data.get("qr_code_watermark", True))
        halve_backs = int(data.get("halve_backs", 0))
        customer_support = bool(data.get("customer_support", False))

        if not name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Name is required",
            )
        if not amount:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Amount is required",
            )
        if not currency:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Currency is required",
            )
        if not duration:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Duration is required",
            )
        if not isinstance(amount, float):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Amount must be a float",
            )

        if not isinstance(duration, int):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Duration must be a number",
            )
        plan = create_payment_plan(name, amount, currency, duration,
                                   unlimited_link_clicks, unlimited_qr_scans,
                                   shortlinks_per_month, qr_codes_per_month,
                                   link_in_bio, analytics_access,
                                   qr_code_customization, qr_code_watermark,
                                   customer_support, halve_backs)
        if not plan:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Payment Plan already exists",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message=f"Payment Plan: {plan.name} Added",
        )
    except Exception as e:
        logger.exception("traceback@user_blp/add_payment_plan")
        logger.error(f"{e}: error@user_blp/add_payment_plan")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# modify payment plan
@admin_blp.route(f"/{USER_PREFIX}/payment_plan/<plan_id>", methods=["PATCH", "DELETE"])
@jwt_required()
def modify_payment_plan(plan_id):
    try:
        if request.method == "DELETE":
            plan, plan_name = delete_payment_plan(plan_id)
            if not plan:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Payment Plan does not exist",
                )
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message=f"Payment Plan: {plan_name} Deleted",
            )
        data = request.get_json()
        name = data.get("name")
        amount = data.get("amount")
        currency = data.get("currency")
        duration = data.get("duration")
        unlimited_link_clicks = data.get("unlimited_link_clicks")
        unlimited_qr_scans = data.get("unlimited_qr_scans")
        shortlinks_per_month = data.get("shortlinks_per_month")
        qr_codes_per_month = data.get("qr_codes_per_month")
        link_in_bio = data.get("link_in_bio")
        analytics_access = data.get("analytics_access")
        qr_code_customization = data.get("qr_code_customization")
        qr_code_watermark = data.get("qr_code_watermark")
        halve_backs = data.get("halve_backs")
        customer_support = data.get("customer_support")

        if amount and not isinstance(amount, float) and not isinstance(amount, int):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Amount must be a float/int",
            )
        if duration and not isinstance(duration, int):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Duration must be a number",
            )
        plan = edit_payment_plan(plan_id, name, amount, currency, duration,
                                 unlimited_link_clicks, unlimited_qr_scans,
                                 shortlinks_per_month, qr_codes_per_month,
                                 link_in_bio, analytics_access,
                                 qr_code_customization, qr_code_watermark,
                                    customer_support, halve_backs
                                 )
        if not plan:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Payment Plan does not exist",
            )
        if isinstance(plan, str):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message=plan,
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message=f"Payment Plan Updated",
        )
    except Exception as e:
        logger.exception("traceback@user_blp/modify_payment_plan")
        logger.error(f"{e}: error@user_blp/modify_payment_plan")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
