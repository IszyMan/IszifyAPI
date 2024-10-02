import unittest
from models.users import Users, UserSession
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import timedelta, datetime
from app_config import create_app, db
from utils import return_access_token


class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        db.create_all()

        user = Users(
            email="john_doe@example.com",
            password="password",
            first_name="john",
            last_name="doe",
            username="johndoe",
        )

        db.session.add(user)
        db.session.commit()

        user.email_verified = True
        db.session.commit()

        self.access_token = return_access_token(user)
        print(self.access_token, "access token")

        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_dashboard(self):
        res = self.client.get("/api/v1/user/dashboard", headers=self.headers)
        self.assertEqual(res.status_code, 200)

    def test_short_url(
        self,
    ):  # comment out this line "request.urlopen(url)" in ahorten_url.py file in models dir, the functions that
        # validates the url
        data = {
            "original_url": "https://www.mygreatlearning.com/blog/top-django-projects/#hospital-management-system"
        }
        res = self.client.post(
            "/api/v1/user/short_url/create", json=data, headers=self.headers
        )
        self.assertEqual(res.status_code, 201)

    def test_create_qr_code(self):
        data = {
            "data": "https://www.mygreatlearning.com/blog/top-django-projects/#hospital-management-system",
            "category": "url",
        }
        res = self.client.post(
            "/api/v1/qr_code/qrcode", json=data, headers=self.headers
        )
        print(res.json, "res.json")
        self.assertEqual(res.status_code, 201)
