import os
from datetime import datetime

from fastapi import APIRouter, Depends, status, Response, Request, Header
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from config.logger import log
from config.settings import settings
from db.session import get_db
from domains.auth.schemas import auth as schema
from domains.auth.services import login as loginService
from domains.auth.services import login as service_login
from domains.auth.services.user_account import users_forms_service
from services.email_service import EmailSchema
from utils.rbac import get_current_user_db

# Authentication module for admins and users
auth_router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@auth_router.post("/token")
def login_for_both_access_and_refresh_tokens(
        request: Request, response: Response,
        subdomain: str = Header(None),
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_current_user_db)
):
    try:
        user_sign_in = loginService.log_user_in(request=request, response=response, db=db, form_data=form_data)
        return user_sign_in

    except HTTPException as ex:
        if ex.status_code == status.HTTP_401_UNAUTHORIZED: log.exception("Login Failed")
        raise HTTPException(status_code=ex.status_code, detail=str(ex.detail))

    except RateLimitExceeded as ex:
        user = users_forms_service.repo.get_by_email(db=db, email=form_data.username)
        if user:
            user.lock_account(lock_time_minutes=10)
            db.commit()

        raise HTTPException(
            status_code=ex.status_code,
            detail="Account locked due to too many attempts, please try again in 10 minutes."
        )

    except:
        log.exception("Unexpected error in login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )


@auth_router.post("/refresh")
def get_new_access_token(
        response: Response, refresh_token: schema.RefreshToken, db: Session = Depends(get_current_user_db)
):
    token_dict = service_login.get_new_access_token(response, refresh_token, db)
    return token_dict


@auth_router.post("/me")
def get_current_user_by_access_token(token: schema.AccessToken, db: Session = Depends(get_current_user_db)):
    get_current_user = service_login.get_current_user_by_access_token(token, db)
    return get_current_user


def send_reset_email(username: str, email: str, reset_link: str) -> EmailSchema:
    ## prepare the email data
    email_data = EmailSchema(
        subject="Password Reset Request",
        email=[email],
        body={
            "system_logo": settings.SYSTEM_LOGO,
            "username": username,  # replace with actual username
            "name": email,
            "reset_link": reset_link,
            "app_name": settings.PROJECT_NAME
        }
    )

    return email_data


@auth_router.get("/intruder/logs", response_class=PlainTextResponse)
def show_intruder_logs(date: str = None):
    """
    Retrieve and display intruder logs for a specified date.
    If no date is provided, retrieve logs for the current date.
    """

    today = datetime.now().strftime("%Y-%m-%d")
    if date is None:
        date = today

    log_filename = f"intruder_log_{date}.txt"
    log_file_path = os.path.join("security/logs/", log_filename)
    log.debug(f"is directory exist: {os.path.exists(log_file_path)}")
    if not os.path.exists(log_file_path): raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Log file not found"
    )

    with open(log_file_path, "r") as log_file:
        log_data = log_file.read()

    return PlainTextResponse(log_data)
