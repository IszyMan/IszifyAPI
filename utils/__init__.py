import random

from flask import jsonify
import uuid
from flask_jwt_extended import create_access_token, get_jwt_identity
import re
from random import randint, choice
import string
import datetime
import hmac
import hashlib
import base64
from io import BytesIO
import time, json, socket
from urllib.request import urlopen
import requests
import string
import secrets
from bs4 import BeautifulSoup

from logger import logger


def return_response(status_code, status=None, message=None, **data):
    res_data = {
        "status": status,
        "message": message,
    }
    res_data.update(data)

    return jsonify(res_data), status_code


def gen_uuid():
    return str(uuid.uuid4())


def return_access_token(user):
    return create_access_token(
        identity=user.id, expires_delta=datetime.timedelta(days=1)
    )


def is_valid_email(email):
    regex = re.compile(
        r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
    )
    if re.fullmatch(regex, email):
        return True
    return False


def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search("[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search("[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search("[0-9]", password):
        return "Password must contain at least one digit"
    if not re.search("[_@$]", password):
        return "Password must contain at least one special character"
    return None


def generate_otp():
    return str(randint(100000, 999999))


def generate_random_string(length=20):
    characters = string.ascii_letters + string.digits
    random_string = "".join(choice(characters) for _ in range(length))
    return random_string


def return_user_dict(user):
    return user.to_dict()


def convert_binary(base64_file):
    try:
        logger.info("got here")
        binary_data = base64.b64decode(base64_file)
        # Convert binary data to a file-like object
        file_like = BytesIO(binary_data)
        logger.info(f"{file_like} file_like from convert_binary")
        return file_like
    except Exception as e:
        logger.error(f"{e}: error from convert_binary")
        return None


def generate_signature(params_to_sign, api_secret):
    try:
        params_to_sign["timestamp"] = int(time.time())
        sorted_params = "&".join(
            [f"{k}={params_to_sign[k]}" for k in sorted(params_to_sign)]
        )
        to_sign = f"{sorted_params}{api_secret}"
        signature = hmac.new(
            api_secret.encode("utf-8"), to_sign.encode("utf-8"), hashlib.sha1
        ).hexdigest()
        logger.info(f"{signature}: signature from generate_signature")
        return signature
    except Exception as e:
        logger.error(f"{e}: error from generate_signature")
        return None


def get_browser_info(request):
    user_agent = request.user_agent
    user_agent = str(user_agent)
    browsers = {
        "Chrome": r"Chrome\/([0-9\.]+)",
        "Firefox": r"Firefox\/([0-9\.]+)",
        "Safari": r"Version\/([0-9\.]+).*Safari",
        "Edge": r"Edge\/([0-9\.]+)",
        "Opera": r"OPR\/([0-9\.]+)",
    }

    browser_name = "Unknown"
    # browser_version = 'Unknown'

    for name, pattern in browsers.items():
        match = re.search(pattern, user_agent)
        if match:
            browser_name = name
            # browser_version = match.group(1)
            break
    return browser_name


def get_computer_name():
    hostname = socket.gethostname()
    return hostname


def get_info(user_ip):
    url = f"http://ipinfo.io/{user_ip}/json"
    response = urlopen(url)
    data = json.load(response)

    ip = data["ip"]
    city = data["city"]
    country = data["country"]

    return ip, city, country


def detect_disposable_email(email):
    try:
        url = f"https://open.kickbox.com/v1/disposable/{email}"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        res = response.json()
        logger.info(f"{res}: result of disposable email")
        return res.get("disposable")
    except Exception as e:
        logger.error(f"{e}: error@disposable_email")
        return "Error"


def user_id_limiter():
    return get_jwt_identity()


def gen_short_code(url_short=False, un_auth=False):
    # length = random.choice([6, 7, 8])
    length = 5
    # Randomly pick an initial from the list and randomly decide upper or lowercase
    if url_short:
        initial = random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I"])
    elif un_auth:
        initial = random.choice(["J", "K", "L", "M", "N", "O", "P", "Q"])
    else:
        initial = random.choice(["R", "S", "T", "U", "V", "W", "X", "Y", "Z"])
    initial = random.choice([initial.lower(), initial.upper()])
    # Define the possible characters for the short code (A-Z, a-z, 0-9)
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    # Generate a random string of the specified length with mixed case
    short_code = "".join(secrets.choice(characters) for _ in range(length))

    return f"{initial}{short_code}"


def get_website_title(url):
    try:
        # Send a GET request to the website
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the title tag and get its text
        title = soup.title.string if soup.title else None
        logger.info(f"{title}: title from getWebsiteTitle")
        return title
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching the URL: {e}")
        return None
    except Exception as e:
        logger.error(f"{e}: error@getWebsiteTitle")
        return None


def return_host_url(host_url):
    # if host url starts with http instead of https
    if host_url.startswith("http://"):
        host_url = host_url.replace("http://", "https://")
    return host_url


# if it starts with https or http, remove it the http/https for example, https://google.com/ should be google.com
def remove_host_url(host_url):
    if host_url.startswith("https://"):
        host_url = host_url.replace("https://", "")
    elif host_url.startswith("http://"):
        host_url = host_url.replace("http://", "")

    # if last character is /, remove it
    if host_url.endswith("/"):
        host_url = host_url[:-1]
    return host_url
