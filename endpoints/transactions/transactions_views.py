from flask import Blueprint, request
from extensions import db
from utils import return_response, gen_reference_number, naira_to_kobo
from logger import logger
from status_res import StatusRes
from http_status import HttpStatus
from . import pay_stack
from flask_jwt_extended import jwt_required, current_user
from crud import (
    get_all_subscriptions,
    get_payment_plans,
    subscribe,
    get_transactions,
    get_one_transaction,
    get_gift_link_by_id,
    get_gift_account_by_id,
    get_bank_details,
    save_transactions,
    update_user_wallet,
    get_user_wallet
)
from datetime import datetime

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
        logger.exception("traceback@transactions_blp/list_banks")
        logger.error(f"{e}: error@transactions_blp/list_banks")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# resolve account number
@transactions_blp.route(f"{TRANSACT_PREFIX}/resolve-account", methods=["POST"])
def resolve_account():
    try:
        data = request.get_json()
        account_number = data.get("account_number")
        bank_code = data.get("bank_code")
        if not account_number or not bank_code:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Account number and bank code is required",
            )
        res, status_code = pay_stack.resolve_account(account_number, bank_code)
        if status_code != 200:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Failed to resolve account",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Account Resolved",
            account=res.get("data"),
        )
    except Exception as e:
        logger.exception("traceback@transactions_blp/resolve_account")
        logger.error(f"{e}: error@transactions_blp/resolve_account")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# verify paystack transaction
@transactions_blp.route(f"{TRANSACT_PREFIX}/verify-transaction", methods=["POST"])
def verify_transaction():
    try:
        data = request.get_json()
        logger.info(f"Data@verify_transaction: {data}")
        reference_number = data.get("reference")
        amount = data.get("amount")
        email = data.get("email")
        goal_id = data.get("goal_id")
        name = data.get("name")
        message = data.get("message")
        account_id = data.get("account_id")

        if not goal_id or account_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Goal id or account id is required",
            )

        if goal_id:
            gift_link = get_gift_link_by_id(goal_id)
            if not gift_link:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Invalid fund goal",
                )
            trans_type = "fund raising"
            user_id = gift_link.user_id
        else:
            gift_account = get_gift_account_by_id(account_id)
            if not gift_account:
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Invalid account",
                )
            trans_type = "donation"
            user_id = gift_account.user_id

        if not reference_number:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Reference number is required",
            )
        res, status_code = pay_stack.verify_transaction(reference_number)
        logger.info(f"{res}: Result of verify transaction, status code: {status_code}")
        if not res:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Failed to verify transaction",
            )
        if status_code != 200:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Transaction failed to verify",
            )

        from celery_config.utils.celery_works import (
            save_transaction_from_verify_transaction,
        )

        # Save the transaction to db
        save_transaction_from_verify_transaction.delay(
            reference_number,
            amount,
            email,
            goal_id,
            name,
            message,
            res,
            user_id,
            trans_type,
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Transaction Verified",
        )
    except Exception as e:
        logger.exception("traceback@transactions_blp/verify_transaction")
        logger.error(f"{e}: error@transactions_blp/verify_transaction")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# subscribe to a plan
@transactions_blp.route(f"{TRANSACT_PREFIX}/subscribe", methods=["POST"])
@jwt_required()
def subscribe_plan():
    try:
        data = request.get_json()
        plan_id = data.get("plan_id")
        status = "active"
        if not plan_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Plan id is required",
            )
        res = subscribe(current_user.id, plan_id, status)
        if not res:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Failed to subscribe to plan",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Plan Subscribed",
        )
    except Exception as e:
        logger.exception("traceback@transactions_blp/subscribe")
        logger.error(f"{e}: error@transactions_blp/subscribe")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get all payment plans
@transactions_blp.route(f"{TRANSACT_PREFIX}/plans", methods=["GET"])
@jwt_required()
def get_all_payment_plans():
    try:
        res = get_payment_plans()
        if not res:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Failed to get payment plans",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Payment plans retrieved",
            plans=res,
        )
    except Exception as e:
        logger.exception("traceback@transactions_blp/get_payment_plans")
        logger.error(f"{e}: error@transactions_blp/get_payment_plans")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get all transactions
@transactions_blp.route(f"{TRANSACT_PREFIX}/transactions", methods=["GET"])
@jwt_required()
def get_all_transactions():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        reference = request.args.get("reference")
        status = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if start_date:
            start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%d-%m-%Y")
        if end_date:
            end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%d-%m-%Y")

        res = get_transactions(
            page, per_page, current_user.id, reference, status, start_date, end_date
        )

        if not res:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Failed to get transactions",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Transactions retrieved",
            **res,
        )
    except Exception as e:
        logger.exception("traceback@transactions_blp/get_transactions")
        logger.error(f"{e}: error@transactions_blp/get_transactions")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# one transaction
@transactions_blp.route(
    f"{TRANSACT_PREFIX}/transaction/<transaction_id>", methods=["GET"]
)
@jwt_required()
def get_transaction(transaction_id):
    try:
        res = get_one_transaction(transaction_id, current_user.id)
        if not res:
            return return_response(
                HttpStatus.INTERNAL_SERVER_ERROR,
                status=StatusRes.FAILED,
                message="Transaction not found",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Transaction retrieved",
            transaction=res,
        )
    except Exception as e:
        logger.exception("traceback@transactions_blp/get_one_transaction")
        logger.error(f"{e}: error@transactions_blp/get_one_transaction")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get subscriptions
@transactions_blp.route(f"{TRANSACT_PREFIX}/subscriptions", methods=["GET"])
@jwt_required()
def get_subscriptions():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        res = get_all_subscriptions(page, per_page, current_user.id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Subscriptions retrieved",
            **res,
        )
    except Exception as e:
        logger.exception("traceback@transactions_blp/get_all_subscriptions")
        logger.error(f"{e}: error@transactions_blp/get_all_subscriptions")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# payout
@transactions_blp.route(f"{TRANSACT_PREFIX}/payout", methods=["POST"])
@jwt_required()
def payout():
    try:
        data = request.get_json()
        logger.info(f"{data}: data from payout")
        bank_details = get_bank_details(current_user.id)
        if not bank_details:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="Please add your bank details",
            )
        amount = data.get("amount")
        reference = gen_reference_number("trans")
        account_name = bank_details.account_name
        account_number = bank_details.account_number
        bank_code = bank_details.bank_code
        bank_name = bank_details.bank_name
        transfer_note = data.get("narration")

        if not amount:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="Amount is required",
            )

        amount = float(amount)

        my_wallet = get_user_wallet(current_user.id)
        if my_wallet.balance < amount:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="Insufficient balance",
            )

        # transfer_receipt, status_code = pay_stack.create_transfer_receipt(
        #     account_name,
        #     account_number,
        #     bank_code,
        # )
        # logger.info(f"{transfer_receipt}: transfer receipt from payout")
        # logger.info(f"{status_code}: status code from payout")
        # if status_code not in [200, 201]:
        #     return return_response(
        #         HttpStatus.FORBIDDEN,
        #         status=StatusRes.FAILED,
        #         message="Failed to create transfer",
        #     )
        # recipient = transfer_receipt["data"]["recipient_code"]
        # logger.info(f"{recipient}: recipient from payout")
        # initiate_trans_res, i_status_code = pay_stack.initiate_transfer(
        #     naira_to_kobo(amount), reference, recipient, transfer_note
        # )
        # logger.info(f"{initiate_trans_res}: response from initiate transfer")
        # logger.info(f"{i_status_code}: status code from initiate transfer")

        # if i_status_code not in [200, 201]:
        #     return return_response(
        #         HttpStatus.FORBIDDEN,
        #         status=StatusRes.FAILED,
        #         message="Failed to initiate transfer",
        #     )

        save_transactions(
            current_user.id,
            transfer_note,
            amount,
            "",
            "payout",
            reference,
            bank_code,
            bank_name,
            account_name,
            account_number,
            "success",
            # response_json=initiate_trans_res,
            response_json={},
        )

        logger.info("Going to update user wallet")

        update_user_wallet(current_user.id, amount, "subtract")
        logger.info("User wallet updated")

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Payout successful",
        )

    except Exception as e:
        logger.exception("traceback@transactions_blp/payout")
        logger.error(f"{e}: error@transactions_blp/payout")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
