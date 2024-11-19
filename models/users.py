from extensions import db
from func import hex_id, generate_otp
from passlib.hash import pbkdf2_sha256 as hasher
from datetime import datetime, timedelta
from utils import generate_random_string, validate_password
from decorators import retry_on_exception


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.Text)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    user_session = db.relationship(
        "UserSession", backref="user", lazy=True, uselist=False, cascade="all, delete"
    )
    qrcodes = db.relationship(
        "QRCodeData", backref="user", lazy=True, cascade="all, delete"
    )

    def __init__(self, email, password, first_name, last_name, username):
        self.email = email.lower()
        self.password = hasher.hash(password)
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.username = username.lower()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return f"<User {self.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name.title(),
            "last_name": self.last_name.title(),
            "username": self.username,
            "email_verified": self.email_verified,
        }


class UserSession(db.Model):
    __tablename__ = "user_session"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    reset_p = db.Column(db.String(50), nullable=True, unique=True)
    otp = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    reset_p_expiry = db.Column(db.DateTime, nullable=True)
    reset_p_invalid = db.Column(db.Boolean, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


@retry_on_exception(retries=3, delay=1)
def authenticate(email, password):
    user = Users.query.filter_by(email=email).first()
    if user and hasher.verify(password, user.password):
        return user
    return None


@retry_on_exception(retries=3, delay=1)
def username_exist(username):
    user = Users.query.filter_by(username=username).first()
    if user:
        return True
    return False


@retry_on_exception(retries=3, delay=1)
def email_exist(email):
    user = Users.query.filter_by(email=email).first()
    if user:
        return True
    return False


@retry_on_exception(retries=3, delay=1)
def create_user(email, password, first_name, last_name, username):
    if email_exist(email):
        return None, "Email already exist"
    if username_exist(username):
        return None, "Username already exist"
    user = Users(email, password, first_name, last_name, username)
    user.save()
    create_otp(user.id)
    return user, None


@retry_on_exception(retries=3, delay=1)
def get_user(email):
    if not email_exist(email):
        return None
    user = Users.query.filter_by(email=email).first()
    return user


@retry_on_exception(retries=3, delay=1)
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


@retry_on_exception(retries=3, delay=1)
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


@retry_on_exception(retries=3, delay=1)
def get_user_by_email(email):
    return Users.query.filter_by(email=email).first()


# def get_user_by_reset_p(reset_p):
#     usersession = UserSession.query.filter_by(reset_p=reset_p).first()
#     return usersession


@retry_on_exception(retries=3, delay=1)
def update_password(user, password):
    user.password = hasher.hash(password)
    user.update()

    return user


@retry_on_exception(retries=3, delay=1)
def current_user_info(user):
    return {
        "id": user.id,
        "first_name": user.first_name.title(),
        "last_name": user.last_name.title(),
        "username": user.username,
        "email": user.email,
        "email_verified": user.email_verified,
    }


@retry_on_exception(retries=3, delay=1)
def get_user_by_id(user_id):
    return Users.query.filter_by(id=user_id).first()


@retry_on_exception(retries=3, delay=1)
def update_user_role(user_id, is_admin, is_super_admin):
    user = get_user_by_id(user_id)
    user.is_admin = is_admin
    user.is_super_admin = is_super_admin
    user.update()
    return user


@retry_on_exception(retries=3, delay=1)
def change_password(current_user, new_password):
    pass_val = validate_password(new_password)
    if pass_val:
        return pass_val
    current_user.password = hasher.hash(new_password)
    current_user.update()
    return None


@retry_on_exception(retries=3, delay=1)
def get_user_by_reset_p(reset_p):
    usersession = UserSession.query.filter_by(reset_p=reset_p).first()
    return usersession.user if usersession else None
