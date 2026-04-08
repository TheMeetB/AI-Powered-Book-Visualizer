import os

from fastapi_mail import ConnectionConfig, FastMail
from pydantic import EmailStr


class MailConfig:
    mail_config = ConnectionConfig(
        MAIL_USERNAME=os.getenv("GOOGLE_MAIL_ID"),
        MAIL_PASSWORD=os.getenv("GOOGLE_MAIL_PASSWORD"),
        MAIL_FROM=EmailStr(os.getenv("GOOGLE_MAIL_ID")),
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_FROM_NAME="Book Visualizer",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True
    )

    fm = FastMail(mail_config)
