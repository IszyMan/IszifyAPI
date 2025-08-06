from functools import wraps
from flask_jwt_extended import current_user
from utils import return_response
from flask import request
from http_status import HttpStatus
from status_res import StatusRes
import time
from datetime import datetime
from sqlalchemy.exc import OperationalError
from extensions import db
from logger import logger
from models.payment import (
    Subscriptions,
    PaymentPlans,
)
from crud import (
    get_current_bio_link_count,
    get_current_shortlink_count,
    get_current_qr_code_count,
)


# email verified decorator
def email_verified(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.email_verified:
            return f(*args, **kwargs)
        else:
            return return_response(
                HttpStatus.UNAUTHORIZED,
                status=StatusRes.FAILED,
                message="Email not verified",
            )

    return decorated_function


# def retry_on_exception(retries=3, delay=1, exceptions=(OperationalError,)):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             for attempt in range(retries):
#                 try:
#                     return func(*args, **kwargs)
#                 except exceptions as e:
#                     if attempt < retries - 1:  # if not the last attempt
#                         print(f"Retrying due to: {e}. Attempt {attempt + 1}/{retries}.")
#                         time.sleep(delay)  # wait before retrying
#                     else:
#                         print(f"Failed after {retries} attempts.")
#                         raise  # re-raise the last exception
#                 finally:
#                     # Rollback the session if there was an exception
#                     if hasattr(args[0], 'session'):
#                         args[0].session.rollback()
#         return wrapper
#
#     return decorator


def retry_on_exception(retries=3, delay=1, exceptions=(OperationalError,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt < retries - 1:
                        logger.info(
                            f"Retrying due to: {e}. Attempt {attempt + 1}/{retries}."
                        )
                        time.sleep(delay)
                    else:
                        logger.info(f"Failed after {retries} attempts.")
                        raise
                finally:
                    db.session.rollback()  # Rollback the session if there was an exception

        return wrapper

    return decorator


def check_qr_code_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "GET":
            return f(*args, **kwargs)
        subscription = (
            Subscriptions.query.filter_by(user=current_user)
            .order_by(Subscriptions.start_date.desc())
            .first()
        )

        if not subscription:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="No active subscription found.",
            )

        plan = PaymentPlans.query.get(subscription.plan_id)

        if not plan:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="Subscription plan not found.",
            )

        current_qr_codes = get_current_qr_code_count(
            current_user
        )  # Function to get current QR code count

        if current_qr_codes >= plan.qr_codes_per_month:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="You have reached your limit for QR codes for the month.",
            )

        return f(*args, **kwargs)

    return decorated_function


def check_shortlink_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        subscription = (
            Subscriptions.query.filter_by(user=current_user)
            .order_by(Subscriptions.start_date.desc())
            .first()
        )

        if not subscription:
            logger.info("No active subscription found.")
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="No active subscription found.",
            )

        plan = PaymentPlans.query.get(subscription.plan_id)

        if not plan:
            logger.info("Subscription plan not found.")
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="Subscription plan not found.",
            )

        current_shortlinks = get_current_shortlink_count(
            current_user
        )  # Function to get current shortlink count

        if current_shortlinks >= plan.shortlinks_per_month:
            logger.info(f"{current_shortlinks} >= {plan.shortlinks_per_month}")
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="You have reached your limit for shortlinks for the month.",
            )

        return f(*args, **kwargs)

    return decorated_function


def check_bio_link_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        subscription = (
            Subscriptions.query.filter_by(user=current_user)
            .order_by(Subscriptions.start_date.desc())
            .first()
        )

        if not subscription:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="No active subscription found.",
            )

        # plan = PaymentPlans.query.get(subscription.plan_id)

        if not subscription.plan:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="Subscription plan not found.",
            )

        current_bio_links = get_current_bio_link_count(
            current_user
        )  # Function to get current bio link count

        if current_bio_links >= subscription.plan.link_in_bio:
            logger.info(f"{current_bio_links} >= {subscription.plan.link_in_bio}")
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="You have reached your limit for bio links for the month.",
            )

        return f(*args, **kwargs)

    return decorated_function


def check_analytics_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        subscription = (
            Subscriptions.query.filter_by(user=current_user)
            .order_by(Subscriptions.start_date.desc())
            .first()
        )

        if not subscription:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="No active subscription found.",
            )

        # plan = PaymentPlans.query.get(subscription.plan_id)

        if not subscription.plan:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="Subscription plan not found.",
            )

        if not subscription.plan.analytics_access:
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="You do not have access to analytics.",
            )

        return f(*args, **kwargs)

    return decorated_function


# check subscription expired
def check_subscription_expired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "GET":
            return f(*args, **kwargs)
        subscription = (
            Subscriptions.query.filter_by(user=current_user)
            .order_by(Subscriptions.start_date.desc())
            .first()
        )

        if not subscription:
            logger.info("No active subscription found.")
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="No active subscription found.",
            )

        if "free" in subscription.plan.name.lower():
            logger.info("Free plan")
            return f(*args, **kwargs)

        if subscription.end_date < datetime.now():
            return return_response(
                HttpStatus.FORBIDDEN,
                status=StatusRes.FAILED,
                message="Your subscription has expired.",
            )

        return f(*args, **kwargs)

    return decorated_function
