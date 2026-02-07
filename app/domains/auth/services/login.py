import json
import os
from datetime import datetime, timezone
from datetime import timedelta

import httpx
from fastapi import Depends, status, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy import text
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from config.logger import log
from config.settings import settings
from db.session import get_db
from domains.auth.models import RefreshToken, Role, User
from domains.auth.respository.user_account import user_actions
from domains.auth.schemas import auth as schema
from domains.auth.services.user_account import users_forms_service
from domains.auth.services.user_account_mail import send_email, account_emergency
from domains.auth.respository.role import role_crud
from utils.core import change_database_schema
from utils.rbac import get_current_user_db
from utils.security import Security


def get_tokens(request: Request):
    # Extract tokens from cookies
    access_token = request.cookies.get("AccessToken")
    refresh_token = request.cookies.get("RefreshToken")

    return {
        "AccessToken": access_token,
        "RefreshToken": refresh_token
    }


def list_logged_in_users(request: Request, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    # Fetch tokens from cookies
    tokens = get_tokens(request)
    if not tokens['AccessToken'] or not tokens['RefreshToken']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")

    user_email = None

    # Verify Access Token
    try:
        payload = Security.decode_token(tokens['AccessToken'])
        user_email = payload.get("sub")
    except JWTError:
        # If Access Token is invalid, try verifying the Refresh Token
        try:
            payload = Security.decode_token(tokens['RefreshToken'])
            user = payload.get("sub")
            if user:
                user_email = user.email  # Extract email from user object
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid tokens")

    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to determine logged-in user")

    # Query to list all users with active refresh tokens
    logged_in_users_query = db.execute(
        select(User)
        .join(RefreshToken, User.id == RefreshToken.user_id)
        .offset(skip)
        .limit(limit)
    )
    logged_in_users = logged_in_users_query.scalars().all()

    # Format the output
    user_list = [
        {
            "user_id": user.id,
            "email": user.email,
            "role_id": user.role_id
        }
        for user in logged_in_users
    ]

    return {"logged_in_users": user_list}


def secure_log_intruder_info(intruder_info: dict):
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file_name = f"intruder_log_{current_date}.txt"
    log_directory = "security/logs/"

    # Secure the logging directory
    # os.makedirs(log_directory, mode=0o750, exist_ok=True)
    os.makedirs(log_directory, exist_ok=True)
    log_filepath = os.path.join(log_directory, log_file_name)

    log_entry = (
        f"Timestamp: {intruder_info.get('timestamp', 'N/A')}\n"
        f"IP Address: {intruder_info.get('ip_address', 'N/A')}\n"
        f"MAC Address: {intruder_info.get('mac_address', 'N/A')}\n"
        f"User-Agent: {intruder_info.get('user_agent', 'N/A')}\n"
        f"Location: {json.dumps(intruder_info.get('location', {}))}\n"
        f"Username Attempted: {intruder_info.get('username', 'N/A')}\n"
        "\n================================================================================\n\n"
    )

    # Use a try-except block to catch potential errors
    try:
        with open(log_filepath, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
    except:
        log.exception("Failed to open log file")


# get location data
def get_location_data(ip_address: str) -> dict:
    try:
        response = httpx.get(f"https://ipinfo.io/{ip_address}/geo")
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
    except:
        log.exception("Failed to get location data")
    return {}


def log_intruder_attempt(username: str, request: Request):
    location = {}
    try:
        response = httpx.get(f"https://ipinfo.io/{request.client.host}/geo")
        response.raise_for_status()

        if response.status_code == 200: location = response.json()

    except:
        log.exception("Failed to get client host location data at log_intruder_attempt")

    intruder_info = {
        "username": username,
        "ip_address": request.client.host,
        "mac_address": request.headers.get("X-MAC-Address", "N/A"),
        "user_agent": request.headers.get("User-Agent", "N/A"),
        "location": location,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Log the intruder information
    return secure_log_intruder_info(intruder_info)


def log_user_in(
        request: Request,
        response: Response,
        db: Session = Depends(get_current_user_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = users_forms_service.repo.get_by_email(db, email=form_data.username)

    if not user: raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )
    if not user.is_active: raise HTTPException(
        status_code=status.HTTP_423_LOCKED,
        detail="Account Disabled, please contact system administrator for redress.",
    )
    now_utc = datetime.now(timezone.utc)

    if user.is_account_locked():
        if now_utc < user.account_locked_until:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is locked due to multiple failed login attempts.",
            )
        else:
            # Unlock the account if the lock time has passed
            user.account_locked_until = None
            db.commit()

    if not Security.verify_password(form_data.password, user.password):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= 3:
            user.lock_account(lock_time_minutes=10)

            if user.lock_count <= 2:
                user.lock_count += 1

            elif user.lock_count >= 3:
                user.is_active = False
                user.lock_count = 0
                db.commit()
                email_body = account_emergency("")
                send_email(email=user.email, subject="Account Status", body=email_body)  # send email message

            db.commit()

            log_intruder_attempt(user.email, request)
            # LoginService.log_intruder_attempt(user.username, request)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is locked due to multiple failed login attempts.",
            )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    is_system_admin = True
    # Reset failed attempts after successful login
    user.reset_failed_attempts()
    db.commit()

    # Token creation logic
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_DURATION_IN_MINUTES)

    if form_data.scopes and "remember_me" in form_data.scopes:
        refresh_token_expires = timedelta(days=60)

    access_token = Security.create_access_token(
        data={"sub": str(user.email)}, expires_delta=access_token_expires
    )
    refresh_token = Security.create_refresh_token(
        data={"sub": str(user)}, expires_delta=refresh_token_expires
    )

    expiration_time = datetime.now() + refresh_token_expires
    access_token_expiration = datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    db_refresh_token = db.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
    db_refresh_token = db_refresh_token.scalars().first()
    if db_refresh_token:
        db_refresh_token.refresh_token = refresh_token
        db_refresh_token.expiration_time = expiration_time
    else:
        db_refresh_token = RefreshToken(user_id=user.id, refresh_token=refresh_token, expiration_time=expiration_time)
        db.add(db_refresh_token)

    db.commit()

    # refresh_token_expires = expiration_time
    # 
    # Set cookies for access and refresh tokens
    response.set_cookie(
        key="AccessToken",
        value=access_token,
        httponly=True,
        secure=True,
        samesite='none',
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    if form_data.scopes and "remember_me" in form_data.scopes:
        response.set_cookie(
            key="RefreshToken",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='none',
            expires=(settings.REFRESH_TOKEN_DURATION_IN_MINUTES + settings.REFRESH_TOKEN_DURATION_IN_MINUTES)
        )
    else:
        response.set_cookie(
            key="RefreshToken",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='none',
            expires=settings.REFRESH_TOKEN_DURATION_IN_MINUTES
        )

    # build response dict
    response = {
        "access_token": access_token,
        "token_type": "bearer",
        "access_token_expiration": access_token_expiration,
        "refresh_token": refresh_token,
        "refresh_token_expiration": expiration_time,
        "user": {
            "id": user.id,
            #"username": user.username,
            "email": user.email,
            "role_id": user.role_id,
            "role": dict(),
            "permissions": []
        }
    }
    if is_system_admin:
        system_admin_role_query = db.execute(select(Role).where(Role.id == user.role_id))
        system_admin_role = system_admin_role_query.scalars().first()
        if system_admin_role:
            response["user"]["role"] = dict(id=system_admin_role.id, name=system_admin_role.name)
        return response


    # get role and permissions, then add those to the response dict also
    account_role = role_crud.get_by_field(db=db, field="id", value=user.role_id, silent=True)
    if account_role:
        response["user"]["role"] = dict(id=account_role.id, name=account_role.name)
        response["user"]["permissions"] = [dict(id=perm.id, name=perm.name) for perm in account_role.permissions]

    return response


def get_new_access_token(
        response: Response,
        refresh_token: schema.RefreshToken,
        db: Session = Depends(get_current_user_db)
):
    refresh_token_check = db.execute(
        select(RefreshToken).where(RefreshToken.refresh_token == refresh_token.refresh_token))
    refresh_token_check = refresh_token_check.scalars().first()
    if not refresh_token_check: raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate new access token credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    user_data = db.execute(select(User).filter(User.id == refresh_token_check.user_id))
    user_data = user_data.scalars().first()
    # Get current user information
    log.debug("user id: ", refresh_token_check.user_id)
    # user_data = users_forms_service.get_user(db=db, id=refresh_token_check.user_id)
    log.debug("user email: ", user_data.email)

    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_DURATION_IN_MINUTES)
    new_access_token = Security.create_access_token(
        data={"sub": str(user_data.email)}, expires_delta=access_token_expires
    )
    new_refresh_token = Security.create_refresh_token(jsonable_encoder(user_data), expires_delta=refresh_token_expires)

    # # Set Cookie for new access token
    # response.set_cookie(
    #     key="AccessToken",
    #     value=new_access_token,
    #     samesite='none',
    #     httponly=True,
    #     expires=settings.COOKIE_ACCESS_EXPIRE,
    #     # domain=settings.COOKIE_DOMAIN,
    #     secure=True
    # )
    # 
    # # Set Cookie for new refresh token
    # response.set_cookie(
    #     key="RefreshToken",
    #     value=new_refresh_token,
    #     samesite='none',
    #     httponly=True,
    #     expires=settings.COOKIE_REFRESH_EXPIRE,
    #     # domain=settings.COOKIE_DOMAIN,
    #     secure=True
    # )

    refresh_token_check = db.execute(
        select(RefreshToken).where(RefreshToken.refresh_token == refresh_token.refresh_token))
    refresh_token_obj = refresh_token_check.scalars().first()  # Extract the ORM instance

    if refresh_token_obj:
        db.delete(refresh_token_obj)
        db.commit()

    refresh_token_dict = {
        "user_id": user_data.id,
        "refresh_token": new_refresh_token,
    }

    # create new refresh token for user after requesting for a new access token
    refresh_token_data = RefreshToken(**refresh_token_dict)
    db.add(refresh_token_data)
    db.commit()

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token,
        "status": status.HTTP_200_OK
    }


def get_current_user_by_access_token(token: schema.AccessToken,
                                     db: Session = Depends(get_current_user_db)):
    refresh_data = Security.verify_access_token(token.access_token)
    log.debug("refresh_data ", refresh_data.email)

    get_user_data = user_actions.get_by_email(db, email=refresh_data.email)

    check_user_role = db.execute(
        select(Role).where(Role.id == get_user_data.role_id)
    )
    check_user_role = check_user_role.scalars().first()

    db_role = {
        "role_id": check_user_role.id,
        "name": check_user_role.name
    }

    return {
        "username": get_user_data.username,
        "id": get_user_data.id,
        "email": get_user_data.email,
        "role": db_role
    }
