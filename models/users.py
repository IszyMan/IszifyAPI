from extensions import db
from func import hex_id, generate_otp
from passlib.hash import pbkdf2_sha256 as hasher


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.Text)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    otp = db.Column(db.String(8), default=generate_otp)
    email_verified = db.Column(db.Boolean, default=False)

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


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user and hasher.verify(password, user.password):
        return user
    return None


def username_exist(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return True
    return False


def email_exist(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return True
    return False


def create_user(email, password, first_name, last_name, username):
    if email_exist(email):
        return None, "Email already exist"
    if username_exist(username):
        return None, "Username already exist"
    user = User(email, password, first_name, last_name, username)
    user.save()
    return user, None


def get_user(email):
    if not email_exist(email):
        return None
    user = User.query.filter_by(email=email).first()
    return user
