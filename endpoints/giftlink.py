from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from crud import (
    save_or_update_bank_details,
    get_bank_details,
    is_valid_enum_value,
    is_slug_exist,
    is_username_exist,
    create_fresh_giftlink,
    create_gift_link,
    get_user_wallet,
    get_gift_links_with_pagination,
    create_gift_account,
    update_gift_account,
    load_gift_link_by_slug,
    # get_all_gift_account,
    get_one_gift_account,
    get_all_gift_links,
    get_gift_account_by_username,
    update_gift_link,
    get_current_user_gift_account,
    get_one_gift_link,
    get_all_transaction_histories,
    get_all_supporters_histories,
)
from utils import return_response
from extensions import db
from logger import logger
from flask_jwt_extended import current_user, jwt_required
from connection.redis_connection import redis_conn
import json
from models.giftlink import GiftType

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
        niche = data.get("niche", [])
        gift_type = data.get("gift_type")
        profile_image = data.get("profile_image")
        cover_image = data.get("cover_image")
        font_style = data.get("font_style")
        color_theme = data.get("color_theme")
        slug = data.get("slug")

        if not all([title, description, gift_type, slug]):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Title, description, gift type and slug are required",
            )

        if is_slug_exist(slug):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="You cannot use this slug",
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
def get_ggift_links():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        gift_type = request.args.get("gift_type")
        slug = request.args.get("slug")
        key = f"gift_links:{current_user.id}:{page}:{per_page}:{gift_type}:{slug}"

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
            current_user.id, page, per_page, gift_type, slug
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


# create gift account
@giftlink_blp.route(f"{GIFT_PREFIX}/create_gift_account", methods=["POST"])
@jwt_required()
def gift_account():
    try:
        data = request.get_json()
        full_name = data.get("full_name")
        username = data.get("username")
        bio = data.get("bio")
        profile_image = data.get("profile_image")
        cover_image = data.get("cover_image")
        website = data.get("website")
        niche = data.get("niche", [])
        # username exist
        if username and is_username_exist(username):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Username already exists",
            )
        if get_current_user_gift_account(current_user.id):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="You already have a gift account",
            )
        create_gift_account(
            current_user.id,
            full_name,
            username,
            bio,
            profile_image,
            cover_image,
            website,
            niche,
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift account created successfully",
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/create_gift_account")
        logger.error(f"{e}: error@giftlink_blp/create_gift_account")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@giftlink_blp.route(f"{GIFT_PREFIX}/get_gift_account", methods=["GET"])
@jwt_required()
def get_gift_account():
    try:
        # page = int(request.args.get("page", 1))
        # per_page = int(request.args.get("per_page", 10))
        giftaccount = get_current_user_gift_account(current_user.id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift account fetched successfully",
            data=giftaccount.to_dict() if giftaccount else {},
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/get_gift_account")
        logger.error(f"{e}: error@giftlink_blp/get_gift_account")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# create or update gift link
@giftlink_blp.route(f"{GIFT_PREFIX}/gift_link/<gift_account_id>", methods=["POST"])
@jwt_required()
def create_fresh_gift_link(gift_account_id):
    try:
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        layout = data.get("layout")
        buy_me = data.get("buy_me")
        tip_unit_price = data.get("tip_unit_price")
        min_price = data.get("min_price")
        button_option = data.get("button_option")
        sugg_amounts = data.get("suggested_amounts", [])
        image = data.get("image")
        link = data.get("link")
        active = data.get("active", True)
        goal_amount = data.get("goal_amount")
        start_amount = data.get("start_amount")
        profile_image = data.get("profile_image")
        cover_image = data.get("cover_image")
        font_style = data.get("font_style")
        color_theme = data.get("color_theme")
        social_links = data.get("social_links", [])
        thanks_msg = data.get("thanks_msg")

        # if gift link is valid
        if not get_one_gift_account(current_user.id, gift_account_id):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Gift account not found",
            )

        create_fresh_giftlink(
            current_user.id,
            gift_account_id,
            title,
            description,
            layout,
            buy_me,
            tip_unit_price,
            min_price,
            button_option,
            sugg_amounts,
            image,
            link,
            active,
            goal_amount,
            start_amount,
            profile_image,
            cover_image,
            font_style,
            color_theme,
            thanks_msg,
            social_links,
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift link created successfully",
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/create_or_update_gift_link")
        logger.error(f"{e}: error@giftlink_blp/create_or_update_gift_link")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get git links by passing gift account id
@giftlink_blp.route(f"{GIFT_PREFIX}/get_gift_links/<gift_account_id>", methods=["GET"])
@jwt_required()
def get_gift_links(gift_account_id):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        if not get_one_gift_account(current_user.id, gift_account_id):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Gift account not found",
            )
        gift_links = get_all_gift_links(
            current_user.id, gift_account_id, page, per_page
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift links fetched successfully",
            data={
                "gift_links": [gift_link.to_dict() for gift_link in gift_links.items],
                "total_items": gift_links.total,
                "total_pages": gift_links.pages,
                "page": page,
                "per_page": per_page,
            },
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


# get gitft links for unauthenticated users
# ======================================================
@giftlink_blp.route(f"{GIFT_PREFIX}/giftlinks/<username>", methods=["GET"])
def get_gift_links_unauth(username):
    try:
        # get current user by username
        gift_account = get_gift_account_by_username(username)
        if not gift_account:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User not found",
            )
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        if not get_one_gift_account(gift_account.user_id, gift_account.id):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Gift account not found",
            )
        gift_links = get_all_gift_links(
            gift_account.user_id, gift_account.id, page, per_page
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift links fetched successfully",
            data={
                "gift_links": [gift_link.to_dict() for gift_link in gift_links.items],
                "total_items": gift_links.total,
                "total_pages": gift_links.pages,
                "page": page,
                "per_page": per_page,
            },
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


@giftlink_blp.route(f"{GIFT_PREFIX}/giftaccount/<username>", methods=["GET"])
def get_gift_account_unauth(username):
    try:
        # page = int(request.args.get("page", 1))
        # per_page = int(request.args.get("per_page", 10))
        gift_account = get_gift_account_by_username(username)
        if not gift_account:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User not found",
            )
        giftaccount = get_current_user_gift_account(gift_account.user_id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift account fetched successfully",
            data=giftaccount.to_dict() if giftaccount else {},
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/get_gift_account")
        logger.error(f"{e}: error@giftlink_blp/get_gift_account")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@giftlink_blp.route(f"{GIFT_PREFIX}/supporters/<username>", methods=["GET"])
def my_supporters(username):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        gift_account = get_gift_account_by_username(username)
        if not gift_account:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User not found",
            )
        supporters, total_supporters = get_all_supporters_histories(
            gift_account.user_id, page, per_page
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Supporters histories fetched successfully",
            data={
                "total_supporters": total_supporters,
                "supporters": [
                    supporter.support_dict() for supporter in supporters.items
                ],
                "total_items": supporters.total,
                "total_pages": supporters.pages,
                "page": page,
                "per_page": per_page,
            },
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/supporters")
        logger.error(f"{e}: error@giftlink_blp/supporters")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


#     ============================================================================
#     ============================================================================


@giftlink_blp.route(
    f"{GIFT_PREFIX}/delete_gift_link/<gift_link_id>", methods=["DELETE"]
)
@jwt_required()
def delete_gift_link(gift_link_id):
    try:
        git_link = get_one_gift_link(current_user.id, gift_link_id)
        if not git_link:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Gift link not found",
            )

        db.session.delete(git_link)
        db.session.commit()
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift link deleted successfully",
        )

    except Exception as e:
        logger.exception("traceback@giftlink_blp/delete_gift_link")
        logger.error(f"{e}: error@giftlink_blp/delete_gift_link")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# edit gift link
@giftlink_blp.route(f"{GIFT_PREFIX}/edit_gift_link/<gift_link_id>", methods=["PATCH"])
@jwt_required()
def edit_gift_link(gift_link_id):
    try:
        data = request.get_json()
        logger.info(f"Data for edit: {data}")
        title = data.get("title")
        description = data.get("description")
        active = data.get("active")
        goal_amount = data.get("goal_amount")
        start_amount = data.get("start_amount")

        # if gift link is valid
        if not get_one_gift_link(current_user.id, gift_link_id):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Gift link not found",
            )

        update_gift_link(
            current_user.id,
            gift_link_id,
            title,
            description,
            active,
            goal_amount,
            start_amount,
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift link edited successfully",
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/edit_gift_link")
        logger.error(f"{e}: error@giftlink_blp/edit_gift_link")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# edit gift account
@giftlink_blp.route(
    f"{GIFT_PREFIX}/edit_gift_account/<gift_account_id>", methods=["PATCH"]
)
@jwt_required()
def edit_gift_account(gift_account_id):
    try:
        data = request.get_json()
        full_name = data.get("full_name")
        username = data.get("username")
        bio = data.get("bio")
        color_theme = data.get("color_theme")
        preset = data.get("preset")
        profile_image = data.get("profile_image")
        cover_image = data.get("cover_image")
        website = data.get("website")
        niche = data.get("niche", [])
        buy_me = data.get("buy_me")
        tip_unit_price = data.get("tip_unit_price")
        min_price = data.get("min_price")
        button_option = data.get("button_option")
        layout = data.get("layout")
        thanks_msg = data.get("thanks_msg")
        sugg_amounts = data.get("suggested_amounts", [])
        standard_amounts = data.get("standard_amounts", [])
        social_links = data.get("social_links", [])

        # if gift account is valid
        user_account = get_one_gift_account(current_user.id, gift_account_id)
        if not user_account:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Gift account not found",
            )

        if (
            username
            and is_username_exist(username)
            and username != user_account.username
        ):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Username already exists",
            )

        update_gift_account(
            current_user.id,
            gift_account_id,
            full_name,
            username,
            bio,
            profile_image,
            cover_image,
            website,
            niche,
            buy_me,
            tip_unit_price,
            min_price,
            button_option,
            sugg_amounts,
            social_links,
            layout,
            thanks_msg,
            color_theme,
            preset,
            standard_amounts,
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Gift account edited successfully",
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/edit_gift_account")
        logger.error(f"{e}: error@giftlink_blp/edit_gift_account")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# transaction histories along with total earnings and outstanding balance
@giftlink_blp.route(f"{GIFT_PREFIX}/transaction_histories", methods=["GET"])
@jwt_required()
def transaction_histories():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        transaction_hists, total_earnings = get_all_transaction_histories(
            current_user.id, page, per_page
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Transaction histories fetched successfully",
            data={
                "total_earnings": total_earnings,
                "outstanding_bal": current_user.user_wallet.balance,
                "transaction_histories": [
                    transaction_history.to_dict()
                    for transaction_history in transaction_hists.items
                ],
                "total_items": transaction_hists.total,
                "total_pages": transaction_hists.pages,
                "page": page,
                "per_page": per_page,
            },
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/transaction_histories")
        logger.error(f"{e}: error@giftlink_blp/transaction_histories")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@giftlink_blp.route(f"{GIFT_PREFIX}/supporters_histories", methods=["GET"])
@jwt_required()
def supporters_histories():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        supporters, total_supporters = get_all_supporters_histories(
            current_user.id, page, per_page
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Supporters histories fetched successfully",
            data={
                "total_supporters": total_supporters,
                "supporters": [
                    supporter.support_dict() for supporter in supporters.items
                ],
                "total_items": supporters.total,
                "total_pages": supporters.pages,
                "page": page,
                "per_page": per_page,
            },
        )
    except Exception as e:
        logger.exception("traceback@giftlink_blp/supporters_histories")
        logger.error(f"{e}: error@giftlink_blp/supporters_histories")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
