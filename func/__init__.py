from random import randint
import uuid


def generate_otp():
    otp = randint(100000, 999999)
    return str(otp)


def hex_id():
    return str(uuid.uuid4())
