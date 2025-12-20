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
            logger.error(f"error@get_all_banks: {e}")
            return None

    def resolve_account(self, account_number, bank_code):
        try:
            logger.info(f"{self.headers}: header from resolve_account")
            url = f"{self.base_url}/bank/resolve?account_number={account_number}&bank_code={bank_code}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            logger.info(
                f"{response.content.decode()}: response content from resolve_account"
            )
            logger.info(f"{response.json()}: response JSON from resolve_account")

            return response.json(), response.status_code

        except requests.exceptions.HTTPError as http_err:
            # Handles HTTP errors (4xx, 5xx)
            logger.exception(f"HTTP error occurred: {http_err}")
            return {}, 500

        except requests.exceptions.RequestException as req_err:
            # Handles other requests exceptions (e.g., connection errors)
            logger.exception(f"Request exception occurred: {req_err}")
            return {}, 500

        except Exception as e:
            # Handles all other exceptions
            logger.exception(f"An error occurred: {e}")
            return {}, 500

    # verify transaction
    def verify_transaction(self, reference):
        try:
            url = f"{self.base_url}/transaction/verify/{reference}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"error@verify_transaction: {e}")
            return None, 500

    # create transfer receipt
    def create_transfer_receipt(self, account_name, account_number, bank_code):
        try:
            data = {
                "type": "nuban",
                "name": account_name,
                "account_number": account_number,
                "bank_code": bank_code,
                "currency": "NGN",
            }
            url = f"{self.base_url}/transferrecipient"
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"error@create_transfer_receipt: {e}")
            return None, 500

    # initiate transfer
    def initiate_transfer(self, amount, reference, recipient, transfer_note):
        try:
            data = {
                "source": "balance",
                "amount": float(amount),
                "reference": reference,
                "recipient": recipient,
                "reason": transfer_note,
            }
            url = f"{self.base_url}/transfer"
            response = requests.post(url, headers=self.headers, json=data)
            logger.info(f"{response.content}: response content from initiate transfer")
            logger.info(f"{response.json()}: response from initiate transfer")
            response.raise_for_status()
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"error@initiate_transfer: {e}")
            return None, 500
