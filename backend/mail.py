from urllib.parse import urljoin

from flask import request
from flask_mailman import Mail, EmailMessage

mail = Mail()


def get_mail_content(pin_code, pin_confirmation_url_part):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            .center-content {{
                display: flex;
                justify-content: center;
            }}
        </style>
      </head>
      <body>
        <div class="center-content">            
            <p>Gib den PIN Code auf der Website ein, oder unter folgendem Link:
            <a href={urljoin(request.base_url, pin_confirmation_url_part)}>PIN Code Link</a>
            </p>
        </div>
        <div class="center-content">
            <p>PIN Code: <strong>{pin_code}</strong></p>
        </div>
      </body>
    </html>
    """


def send_pin_code(email: str, pin_code: str, pin_confirmation_url_part: str):
    msg = EmailMessage(
        subject="Max'au Beach Master of Desaster - PIN Code",
        body=get_mail_content(pin_code, pin_confirmation_url_part),
        from_email="admin@testdomain",
        to=[email],
    )
    msg.content_subtype = "html"
    msg.send()
