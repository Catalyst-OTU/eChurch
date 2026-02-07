from datetime import datetime, timedelta
from typing import Optional

from fastapi import status, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from config.settings import settings
from domains.auth.models.users import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class Security:

    @staticmethod
    def get_user_by_email(username: str, db: Session):
        user = db.execute(select(User).where(User.email == username))
        user = user.scalars().first()
        if not user:
            return False
        return user

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    # function to authenticate user
    @staticmethod
    def authenticate_user(username: str, password: str, db: Session):
        db_user = Security.get_user_by_email(username=username, db=db)
        if not db_user:
            return False
        if not Security.verify_password(password, db_user.password):
            return False
        return db_user

    # function to get hash password
    @staticmethod
    def get_password_hash(password='password'):
        return pwd_context.hash(password)

    # Generate access token function
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    # Generate reset password token function
    @staticmethod
    def generate_reset_password_token(expires: int = None):
        if expires is not None:
            expires = datetime.utcnow() + expires
        else:
            expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"exp": expires}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_access_token(token: str = Depends(oauth2_scheme)):
        # access_token = request.cookies.get('AccessToken')

        # if access_token is None: raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Access token is invalidated"
        # )
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            # log.debug("username/email extracted is ", username)

        except JWTError:
            raise credentials_exception
        user = User(email=username)
        if user is None:
            raise credentials_exception
        return user

    # Generate refresh access token function
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str):
        try:
            # print("token in decode_token: ", token)
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
            # print("\npayload in decode_token: ", payload)
            return payload
        except JWTError:
            return None
