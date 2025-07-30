from models.admin_models import Admin, Roles
from passlib.hash import pbkdf2_sha256 as hasher
from extensions import db


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
    admin.delete()
    return True


def get_one_admin(admin_id):
    admin = Admin.query.filter_by(id=admin_id).first()
    return admin


def get_all_admins(
    page,
    per_page,
    active=None,
    start_date=None,
    end_date=None,
    fullname=None,
    email=None,
    changed_password=None,
    role_id=None,
):
    filters = []

    if active is not None:
        filters.append(Admin.active == active)
    if start_date and end_date:
        filters.append(Admin.created.between(start_date, end_date))
    if fullname:
        filters.append(
            Admin.first_name.ilike(f"%{fullname}%")
            | Admin.last_name.ilike(f"%{fullname}%")
        )
    if email:
        filters.append(Admin.email.ilike(f"%{email}%"))
    if changed_password is not None:
        filters.append(Admin.changed_password == changed_password)
    if role_id is not None:
        filters.append(Admin.role_id == role_id)

    admins = (
        Admin.query.filter(*filters)
        .order_by(Admin.created.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

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


def get_one_role(role_id):
    return Roles.query.filter(Roles.id == role_id).first()
