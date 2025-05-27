from datetime import datetime, timedelta

from passlib.hash import pbkdf2_sha256 as hasher

from models.users import Users, UserSession
from utils import generate_otp, generate_random_string


def authenticate(email, password):
    user = Users.query.filter_by(email=email).first()
    if user and hasher.verify(password, user.password):
        return user
    return None


def username_exist(username):
    user = Users.query.filter_by(username=username).first()
    if user:
        return True
    return False


def email_exist(email):
    user = Users.query.filter_by(email=email).first()
    if user:
        return True
    return False


def create_user(email, password, first_name, last_name, username):
    if email_exist(email):
        return None, "Email already exist"
    if username_exist(username):
        return None, "Username already exist"
    user = Users(email, password, first_name, last_name, username)
    user.save()
    create_otp(user.id)
    return user, None


def get_user(email):
    if not email_exist(email):
        return None
    user = Users.query.filter_by(email=email).first()
    return user


def create_otp(user_id):
    # expiry time is 10 minutes
    expiry = datetime.now() + timedelta(minutes=10)
    otp = generate_otp()
    usersession = UserSession.query.filter_by(user_id=user_id).first()
    if usersession:
        usersession.otp = otp
        usersession.otp_expiry = expiry
        usersession.update()
    else:
        usersession = UserSession(user_id=user_id, otp=otp, otp_expiry=expiry)
        usersession.save()
    return usersession


def create_reset_p(user_id):
    # expiry time is 10 minutes
    expiry = datetime.now() + timedelta(minutes=10)
    reset_p = f"ly{generate_random_string()}"
    usersession = UserSession.query.filter_by(user_id=user_id).first()
    if usersession:
        usersession.reset_p = reset_p
        usersession.reset_p_expiry = expiry
        usersession.reset_p_invalid = False
        usersession.update()
    else:
        usersession = UserSession(
            user_id=user_id, reset_p=reset_p, reset_p_expiry=expiry
        )
        usersession.save()
    return usersession


def get_user_by_email(email):
    return Users.query.filter_by(email=email).first()


# def get_user_by_reset_p(reset_p):
#     usersession = UserSession.query.filter_by(reset_p=reset_p).first()
#     return usersession


def update_password(user, password):
    user.password = hasher.hash(password)
    user.update()

    return user


def current_user_info(user):
    return {
        "id": user.id,
        "first_name": user.first_name.title(),
        "last_name": user.last_name.title(),
        "username": user.username,
        "email": user.email,
        "email_verified": user.email_verified,
    }


def get_user_by_id(user_id):
    return Users.query.filter_by(id=user_id).first()


def update_user_role(user_id, is_admin, is_super_admin):
    user = get_user_by_id(user_id)
    user.is_admin = is_admin
    user.is_super_admin = is_super_admin
    user.update()
    return user


def change_password(current_user, new_password):
    pass_val = validate_password(new_password)
    if pass_val:
        return pass_val
    current_user.password = hasher.hash(new_password)
    current_user.update()
    return None


def get_user_by_reset_p(reset_p):
    usersession = UserSession.query.filter_by(reset_p=reset_p).first()
    return usersession.user if usersession else None
