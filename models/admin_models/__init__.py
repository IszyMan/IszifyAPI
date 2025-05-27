from extensions import db
from func import hex_id, generate_otp
from passlib.hash import pbkdf2_sha256 as hasher
from datetime import datetime, timedelta
from utils import generate_random_string, validate_password


# roles
class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100), unique=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    admin = db.relationship(
        "Admin", backref="role", lazy=True, uselist=False, cascade="all, delete"
    )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.Text)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    changed_password = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.String(50), db.ForeignKey("roles.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    admin_session = db.relationship(
        "AdminSession", backref="admin", lazy=True, uselist=False, cascade="all, delete"
    )

    def __init__(self, email, password, first_name, last_name):
        self.email = email.lower()
        self.password = hasher.hash(password)
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name.title(),
            "last_name": self.last_name.title(),
            "active": self.active,
            "changed_password": self.changed_password,
            "role": self.role.name.title(),
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<User {self.email}>"


class AdminSession(db.Model):
    __tablename__ = "admin_session"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    admin_id = db.Column(db.String(50), db.ForeignKey("admin.id"), nullable=False)
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
