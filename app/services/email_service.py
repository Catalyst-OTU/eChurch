import asyncio
from typing import List, Dict

# from jinja2 import Environment, select_autoescape, PackageLoader
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Environment, select_autoescape, FileSystemLoader
from pydantic import BaseModel, EmailStr

from config.settings import settings
from domains.auth.models.users import User

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailSchema(BaseModel):
    subject: str
    email: List[EmailStr]
    body: Dict[str, str]


class Email:
    def __init__(self, user: User, url: str, email: EmailSchema):

        self.name = user.username
        self.sender = settings.MAIL_USERNAME
        self.email = email
        self.url = url

    @staticmethod
    def sendMailService(data: EmailSchema, template_name: str) -> JSONResponse:
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

        try:
            # load the html template
            template = env.get_template(template_name)

            ## Render the template with the data provided in 'body'
            html_content = template.render(data.body)

            # html = template.render(
            #     url=self.url,
            #     name=self.name,
            #     email=self.email,
            #     subject=subject

            # )

            # Define the message options
            message = MessageSchema(
                subject=data.subject,
                recipients=data.email,
                body=html_content,
                subtype="html",

            )

            # Send the email using FastMail
            fm = FastMail(conf)
            asyncio.run(fm.send_message(message, template_name=template_name))
            return JSONResponse(status_code=200, content={"message": "Email has been sent."})

        except Exception as e:
            # Log the exception or handle it appropriately
            print(f"Failed to send email: {str(e)}")
            return JSONResponse(status_code=500, content={"message": "Failed to send email."})
