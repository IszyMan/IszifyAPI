from flask_mail import Message
from flask import render_template
from extensions import mail
from utils import generate_otp


def send_mail(payload):
    msg = Message(
        subject=payload["subject"],
        sender="Izly <iszify.send@gmail.com>",
        recipients=[payload["email"]],
    )

    if payload.get("template_name"):
        msg.html = render_template(payload["template_name"], **payload)
    elif payload.get("body"):
        msg.body = payload["body"]
    else:
        raise ValueError("Either template_name or body must be provided")

    mail.send(msg)
    return True
