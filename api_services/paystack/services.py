from .base import PaystackBase
import requests
from logger import logger


class PaystackClient(PaystackBase):
    def get_all_banks(self):
        try:
            url = f"{self.base_url}/bank?country={self.country}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"error {e}")
            return None

    def resolve_account(self, account_number, bank_code):
        try:
            print(self.headers, "header from resolve_account")
            url = f"{self.base_url}/bank/resolve?account_number={account_number}&bank_code={bank_code}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            print(response.content.decode(), "response content from resolve_account")
            print(response.json(), "response JSON from resolve_account")

            return response.json(), response.status_code

        except requests.exceptions.HTTPError as http_err:
            # Handles HTTP errors (4xx, 5xx)
            print(f"HTTP error occurred: {http_err}")
            return {}, 500

        except requests.exceptions.RequestException as req_err:
            # Handles other requests exceptions (e.g., connection errors)
            print(f"Request exception occurred: {req_err}")
            return {}, 500

        except Exception as e:
            # Handles all other exceptions
            print(f"An error occurred: {e}")
            return {}, 500

    # verify transaction
    def verify_transaction(self, reference):
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"error {e}")
            return None, 500
