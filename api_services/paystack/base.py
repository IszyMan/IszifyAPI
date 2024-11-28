import os

class PaystackBase:
    def __init__(self):
        self.secret_key = os.environ.get("PAYSTACK_SECRET_KEY")
        self.base_url = os.environ.get("PAYSTACK_BASE_URL")
        self.headers = {"Authorization": f"Bearer {self.secret_key}"}
        self.country = os.environ.get("PAYSTACK_COUNTRY")
