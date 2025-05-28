from flask_mail import Message
from flask import render_template_string
from extensions import mail
import os
from dotenv import load_dotenv
import requests
from jinja2 import Environment, FileSystemLoader

load_dotenv()

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
        with open(template_path, "r") as f:
            template_content = f.read()

        # Render the template content using payload
        msg.html = render_template_string(template_content, **payload)
    elif payload.get("body"):
        msg.body = payload["body"]
    else:
        raise ValueError("Either template_name or body must be provided")

    mail.send(msg)
    return True


# Point to the base directory (your-project-root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")


def send_html_email(
    recipients, subject, html_content=None, template_path=None, template_context=None
):
    if template_path:
        try:
            # Setup Jinja2 environment pointing to the templates directory
            env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
            template = env.get_template(template_path)  # e.g., 'welcome.html'
            html_content = template.render(template_context or {})
        except Exception as e:
            print(e)

    url = os.environ.get("ZEPTOMAIL_API_URL")
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": os.environ.get("ZEPTOMAIL_API_KEY"),
    }

    payload = {
        "from": {
            "address": os.environ.get("ZEPTOMAIL_FROM_ADDRESS"),
            "name": os.environ.get("ZEPTOMAIL_FROM_NAME"),
        },
        "bcc": [
            {
                "email_address": {
                    "address": recipient["email"],
                    "name": recipient["name"],
                }
            }
            for recipient in recipients
        ],
        "subject": subject,
        "htmlbody": html_content,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print(response.content)
        return {"status": "success", "response": response.json()}
    except requests.exceptions.RequestException as e:
        print(response.content)
        return {"status": "error", "message": str(e)}
