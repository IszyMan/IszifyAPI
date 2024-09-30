import os
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))

uri = f"""postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get(
    'POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}:{os.environ.get(
    'POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}?sslmode=require"""


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hard to guess string"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # jtw config
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "hard to guess string"
    # expiring time
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'iszify.sqlite')
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


config_obj = {"development": DevelopmentConfig, "testing": TestConfig}
