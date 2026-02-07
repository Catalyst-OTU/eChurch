from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from config.logger import log
from config.settings import settings

# Define the email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)


def send_email(email: EmailStr, subject: str, body: str):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="html"
        )
        fm = FastMail(conf)
        fm.send_message(message)
    except:
        # Log the exception or retry
        log.exception(f"Failed to send email to {email}")


def account_emergency(heading: str = None) -> str:
    if not heading:
        heading = "GI-KACE APPRAISAL SYSTEM"
    return f"""
    <h2>{heading}</h2>
    <p>Your account has been <strong>disabled</strong> due to multiple intrusion attempts.</p>
    <p>Please contact the System's Administrator for redress.</p>

    <p>Thank you.</p>
    """
