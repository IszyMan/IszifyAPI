from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from crud import (
    save_or_update_bank_details,
    get_bank_details,
    is_valid_enum_value,
    is_slug_exist,
    create_gift_link,
    get_user_wallet,
    get_gift_links_with_pagination,
    load_gift_link_by_slug,
)
from utils import return_response
from extensions import db
from logger import logger
from flask_jwt_extended import current_user, jwt_required
from connection.redis_connection import redis_conn
import json
from models.giftlink import NicheEnum, GiftType

GIFT_PREFIX = "giftlink"

giftlink_blp = Blueprint("giftlink_blp", __name__)


@giftlink_blp.route(f"{GIFT_PREFIX}/bank_details", methods=["GET", "POST"])
@jwt_required()
def user_bank_details():
    try:
        if request.method == "POST":
            data = request.get_json()

            logger.info(f"data: {data}")

            bank_code = data.get("bank_code")
            bank_name = data.get("bank_name")
            account_name = data.get("account_name")
            account_number = data.get("account_number")

            if get_bank_details(current_user.id):
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="You have already saved your bank details",
                )

            if not any([bank_code, bank_name, account_name, account_number]):
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="All fields are required",
                )

            bank_details = save_or_update_bank_details(
                bank_code, bank_name, account_name, account_number, current_user.id
            )
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Bank details saved successfully",
                data=bank_details.to_dict(),
            )
        elif request.method == "GET":
            key = f"bank_details:{current_user.id}"
            cached_data = redis_conn.get(key)

            if cached_data:
                bank_details = json.loads(cached_data)
                return return_response(
                    HttpStatus.OK,
                    status=StatusRes.SUCCESS,
                    message="Bank details fetched successfully",
                    data=bank_details,
                )
            bank_details = get_bank_details(current_user.id)

            if bank_details:
                redis_conn.set(key, json.dumps(bank_details.to_dict()), 2000)
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Bank details fetched successfully",
                data=bank_details.to_dict() if bank_details else {},
            )
        else:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid request method",
            )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/bank_details")
        logger.error(f"{e}: error@giftlink_blp/bank_details")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# create gift link
@giftlink_blp.route(f"{GIFT_PREFIX}/create", methods=["POST"])
@jwt_required()
def create_giftlink():
    try:
        data = request.get_json()
        link = data.get("link")
        title = data.get("title")
        description = data.get("description")
        image = data.get("image")
        goal_amount = float(data.get("goal_amount", 0))
        niche = data.get("niche")
        gift_type = data.get("gift_type")
        profile_image = data.get("profile_image")
        cover_image = data.get("cover_image")
        font_style = data.get("font_style")
        color_theme = data.get("color_theme")
        slug = data.get("slug")

        if not all([title, description, niche, gift_type, slug]):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Title, description, niche, gift type and slug are required",
            )

        if is_slug_exist(slug):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="You cannot use this slug",
            )

        # validate niche from NicheEnum
        if not is_valid_enum_value(niche, NicheEnum):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid niche",
            )

        # validate gift type from GiftType
        if not is_valid_enum_value(gift_type, GiftType):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid gift type",
            )

        if gift_type.lower() == "fundraising":
            if not goal_amount:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Goal amount is required for fundraising",
                )

        goal_amount = 0 if gift_type.lower() == "gift" else goal_amount

        create_gift_link(
            current_user.id,
            gift_type,
            niche,
            title,
            description,
            image,
            link,
            goal_amount,
            profile_image,
            cover_image,
            font_style,
            color_theme,
            slug,
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift Link created successfully",
        )
    except Exception as e:
        logger.exception("error@giftlink_blp/create_gift_link")
        logger.error(f"{e}: error@giftlink_blp/create_gift_link")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get user wallet
@giftlink_blp.route(f"{GIFT_PREFIX}/wallet", methods=["GET"])
@jwt_required()
def get_wallet():
    try:
        cached_data = redis_conn.get(f"wallet:{current_user.id}")
        if cached_data:
            wallet = json.loads(cached_data)
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Wallet fetched successfully",
                data=wallet,
            )
        wallet = get_user_wallet(current_user.id)
        redis_conn.set(f"wallet:{current_user.id}", json.dumps(wallet.to_dict()), 2000)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Wallet fetched successfully",
            data=wallet.to_dict(),
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/get_wallet")
        logger.error(f"{e}: error@giftlink_blp/get_wallet")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get git links with pagination and filters
@giftlink_blp.route(f"{GIFT_PREFIX}/get_gift_links", methods=["GET"])
@jwt_required()
def get_gift_links():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        niche = request.args.get("niche")
        gift_type = request.args.get("gift_type")
        slug = request.args.get("slug")
        key = (
            f"gift_links:{current_user.id}:{page}:{per_page}:{niche}:{gift_type}:{slug}"
        )

        cached_data = redis_conn.get(key)

        if cached_data:
            logger.info("cache hit")
            gift_dict = json.loads(cached_data)
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Gift links fetched successfully",
                **gift_dict,
            )
        g_links = get_gift_links_with_pagination(
            current_user.id, page, per_page, niche, gift_type, slug
        )
        gift_dict = {
            "gift_links": [gift.to_dict() for gift in g_links.items],
            "total_items": g_links.total,
            "total_pages": g_links.pages,
            "page": page,
            "per_page": per_page,
            "has_next": g_links.has_next,
            "has_prev": g_links.has_prev,
        }

        redis_conn.set(key, json.dumps(gift_dict))
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift links fetched successfully",
            **gift_dict,
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/get_gift_links")
        logger.error(f"{e}: error@giftlink_blp/get_gift_links")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# load gift link to user using slug
@giftlink_blp.route(f"{GIFT_PREFIX}/load/<string:slug>", methods=["GET"])
def load_gift_link(slug):
    try:
        key = f"user_load_gift_link:{slug}"
        cached_data = redis_conn.get(key)
        if cached_data:
            logger.info("cache hit")
            gift_link = json.loads(cached_data)
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Gift link loaded successfully",
                data=gift_link,
            )
        gift_link = load_gift_link_by_slug(slug)
        if not gift_link:
            return return_response(
                HttpStatus.NOT_FOUND,
                status=StatusRes.FAILED,
                message="Invalid URL",
            )
        redis_conn.set(key, json.dumps(gift_link.user_to_dict()), 2000)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift link loaded successfully",
            data=gift_link.user_to_dict(),
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/load_gift_link")
        logger.error(f"{e}: error@giftlink_blp/load_gift_link")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
