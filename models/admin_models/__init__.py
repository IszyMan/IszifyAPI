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


def admin_authenticate(email, password):
    admin = Admin.query.filter_by(email=email).first()
    if admin and hasher.verify(password, admin.password):
        return admin
    return None


def check_email_role_exist(email=None, role_id=None, exist_admin=None):
    if email:
        admin = Admin.query.filter_by(email=email.lower()).first()
        if admin and admin != exist_admin:
            return "Email already exist"

    if role_id:
        role = Roles.query.filter_by(id=role_id).first()
        if not role:
            return "Role does not exist"
    return None


def create_admin_account(email, password, first_name, last_name, role_id):
    admin = Admin(email, password, first_name, last_name)
    admin.role_id = role_id
    admin.save()
    return admin


def edit_one_admin(admin_id, email, first_name, last_name, role_id):
    admin = Admin.query.filter_by(id=admin_id).first()
    if not admin:
        return False

    admin.email = email or admin.email
    admin.first_name = first_name or admin.first_name
    admin.last_name = last_name or admin.last_name
    admin.role_id = role_id or admin.role_id
    admin.update()
    return admin

def delete_one_admin(admin_id):
    admin = Admin.query.filter_by(id=admin_id).first()
    if not admin:
        return "Admin does not exist"
    admin.delete()
    return True

def get_one_admin(admin_id):
    admin = Admin.query.filter_by(id=admin_id).first()
    return admin


def get_all_admins(page, per_page, active=None, start_date=None,
                   end_date=None, fullname=None, email=None, changed_password=None, role_id=None):
    filters = []

    if active is not None:
        filters.append(Admin.active == active)
    if start_date and end_date:
        filters.append(Admin.created.between(start_date, end_date))
    if fullname:
        filters.append(Admin.first_name.ilike(f"%{fullname}%") | Admin.last_name.ilike(f"%{fullname}%"))
    if email:
        filters.append(Admin.email.ilike(f"%{email}%"))
    if changed_password is not None:
        filters.append(Admin.changed_password == changed_password)
    if role_id is not None:
        filters.append(Admin.role_id == role_id)

    admins = Admin.query.filter(*filters).order_by(Admin.created.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return admins


def get_all_roles():
    roles = Roles.query.all()
    return roles


def save_role(name):
    if Roles.query.filter(Roles.name.ilike(name)).first():
        return False
    role = Roles(name)
    role.save()
    return role
