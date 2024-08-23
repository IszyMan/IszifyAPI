import unittest
from models.users import Users, UserSession
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import timedelta, datetime
from app_config import create_app, db


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

        user_session = UserSession(
            user=user,
            otp="123456",
            otp_expiry=datetime.now() + timedelta(minutes=10),
            reset_p="lyTU628jhfM83j",
            reset_p_expiry=datetime.now() + timedelta(minutes=10),
        )

        db.session.add_all([user, user_session])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_model(self):
        user = Users.query.filter_by(email="john_doe@example.com").first()
        self.assertEqual(user.email, "john_doe@example.com")
        self.assertTrue(sha256.verify("password", user.password))

    def test_user_registration(self):
        data = {
            "email": "john_doe2@example.com",
            "password": "Password@01",
            "first_name": "john",
            "last_name": "doe",
            "username": "johndoe2",
        }
        res = self.client.post("/api/v1/auth/register", json=data)
        self.assertEqual(res.status_code, 201)

        user = Users.query.filter_by(email="john_doe2@example.com").first()
        self.assertEqual(user.email, "john_doe2@example.com")
        self.assertTrue(sha256.verify("Password@01", user.password))

    def test_user_verify_account(self):
        data = {
            "email": "john_doe@example.com",
            "otp": "123456",
        }
        res = self.client.patch("/api/v1/auth/verify-account", json=data)
        self.assertEqual(res.status_code, 200)

    def test_user_login(self):
        data = {
            "email": "john_doe@example.com",
            "password": "password",
        }
        user = Users.query.filter_by(email="john_doe@example.com").first()
        user.email_verified = True
        db.session.commit()
        res = self.client.post("/api/v1/auth/login", json=data)
        print(res.data, "data")
        self.assertEqual(res.status_code, 200)

    def test_forgot_password(self):
        data = {
            "email": "john_doe@example.com",
            "frontend_url": "http://localhost:3000/reset-password",
        }
        res = self.client.patch("/api/v1/auth/forgot-password-request", json=data)
        res_dict = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res_dict['user_email'], "john_doe@example.com")

    def test_reset_password(self):
        data = {
            "new_password": "Password@01",
            "confirm_password": "Password@01",
        }
        res = self.client.patch("/api/v1/auth/reset-password/lyTU628jhfM83j", json=data)
        self.assertEqual(res.status_code, 200)
