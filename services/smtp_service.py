from flask_mail import Message
from flask import render_template_string
from extensions import mail
import os

base_dir = os.path.abspath(os.path.dirname(__file__))


def send_mail(payload):
    msg = Message(
        subject=payload["subject"],
        sender="Izly <iszify.send@gmail.com>",
        recipients=[payload["email"]],
    )

    if payload.get("template_name"):
        # Construct the full path to the template
        template_path = os.path.join(base_dir, "../templates", payload["template_name"])

        # Read the template file manually
        with open(template_path, 'r') as f:
            template_content = f.read()

        # Render the template content using payload
        msg.html = render_template_string(template_content, **payload)
    elif payload.get("body"):
        msg.body = payload["body"]
    else:
        raise ValueError("Either template_name or body must be provided")

    mail.send(msg)
    return True
