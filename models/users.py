from extensions import db
from func import hex_id, generate_otp
from passlib.hash import pbkdf2_sha256 as hasher
from datetime import datetime, timedelta
from utils import generate_random_string, validate_password


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

    transactions = db.relationship(
        "Transactions", backref="user", lazy=True, cascade="all, delete"
    )

    subscriptions = db.relationship(
        "Subscriptions", backref="user", lazy=True, cascade="all, delete"
    )

    url_short = db.relationship(
        "Urlshort", backref="user", lazy=True, cascade="all, delete"
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
