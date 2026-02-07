import random
import string

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.respository.user_account import user_actions
from domains.auth.schemas.password_reset import ResetPasswordRequest


class PasswordResetService:
    @staticmethod
    def generate_reset_token():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=50))

    @staticmethod
    def get_current_user_email(schemas: ResetPasswordRequest, db: Session = Depends(get_db)):
        user = user_actions.get_by_email(db, email=schemas.email)
        if not user: raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
        return user


password_reset_service = PasswordResetService
