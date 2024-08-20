from functools import wraps
from flask_jwt_extended import current_user
from utils import return_response
from http_status import HttpStatus
from status_res import StatusRes


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
