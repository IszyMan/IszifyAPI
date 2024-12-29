from .base import PaystackBase
import requests


class PaystackClient(PaystackBase):
    def get_all_banks(self):
        try:
            url = f"{self.base_url}/bank?country={self.country}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print("error", e)
            return None

    # verify transaction
    def verify_transaction(self, reference):
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print("error", e)
            return None
