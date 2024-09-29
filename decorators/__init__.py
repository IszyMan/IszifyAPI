from functools import wraps
from flask_jwt_extended import current_user
from utils import return_response
from http_status import HttpStatus
from status_res import StatusRes
import time
from sqlalchemy.exc import OperationalError


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


def retry_on_exception(retries=3, delay=1, exceptions=(OperationalError,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt < retries - 1:  # if not the last attempt
                        print(f"Retrying due to: {e}. Attempt {attempt + 1}/{retries}.")
                        time.sleep(delay)  # wait before retrying
                    else:
                        print(f"Failed after {retries} attempts.")
                        raise  # re-raise the last exception

        return wrapper

    return decorator
