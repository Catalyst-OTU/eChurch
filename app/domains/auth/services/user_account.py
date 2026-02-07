from typing import List, Optional, Literal
from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session
from config.settings import settings
from domains.auth.models import User
from domains.auth.respository.user_account import user_actions as user_repo
from domains.auth.schemas.user_account import UserSchema, UserCreate, UserUpdate
from domains.auth.services.password_reset import password_reset_service
from services.email_service import Email


class UserService:

    def __init__(self):
        self.repo = user_repo

    def get_organization_admin(self, db: Session, organization_id: UUID4, silent=False) -> Optional[User]:
        admin = self.repo.get_by_filters(  # get the first account created which should be admin account
            db=db, organization_id=organization_id,
            order_by='created_date', order_direction='desc'
        )

        if admin and len(admin) > 0: return admin[0]
        if silent: return None
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    def is_email_taken(self, db: Session, *, email: str, exclude_id: UUID4 = None, silent=True) -> bool:
        is_email_taken = self.repo.is_email_taken(db=db, email=email, exclude_id=exclude_id)
        if is_email_taken and not silent: raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already taken"
        )
        return is_email_taken

    def list_users(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[UserSchema]:
        users = self.repo.get_all(
            db=db, skip=skip, limit=limit,
            order_by=order_by, order_direction=order_direction
        )
        return users

    def create_user(self, user_in: UserCreate, db: Session) -> UserSchema:
        """Creates a new user under an organization and returns the user with role details."""
        unique_fields = ["email"]

        user_db = self.repo.create(db=db, data=user_in, unique_fields=unique_fields)

        token = password_reset_service.generate_reset_token()
        user_db.reset_password_token = token
        db.commit()
        #  Send email with the reset link
        reset_link = f"{settings.FRONTEND_URL}/login/resetpassword?token={token}"

        # email_data = send_reset_email(user_in.username, user_in.email, reset_link)
        # Email.sendMailService(email_data, template_name='password_reset.html')
        return user_db

    def create_organization_superuser(
            self, user_in: UserCreate, db: Session, organization_access_url: str
    ) -> UserSchema:
        """Creates a new admin user for an organization and send the administrator set password email."""
        #organization_service.repo.get_by_id(db=db, id=user_in.organization_id)
        unique_fields = ["email"]

        user_db = self.repo.create(db=db, data=user_in, unique_fields=unique_fields)

        token = password_reset_service.generate_reset_token()
        user_db.reset_password_token = token
        db.commit()
        #  Send email with the reset link
        reset_link = f"{organization_access_url}/login/resetpassword?token={token}"

        from domains.auth.apis.login import send_reset_email

        email_data = send_reset_email(user_in.username, str(user_in.email), reset_link)
        Email.sendMailService(email_data, template_name='admin_password_reset.html')
        return user_db

    def update_user(self, db: Session, *, id: UUID4, user_in: UserUpdate) -> UserSchema:
        user = self.repo.get_by_id(db=db, id=id)
        user = self.repo.update(db=db, db_obj=user, data=user_in)
        return user

    def get_user(self, db: Session, *, id: UUID4) -> UserSchema:
        user = self.repo.get_by_id(db=db, id=id)
        return user

    def delete_user(self, db: Session, *, id: UUID4) -> None:
        self.repo.get_by_id(db=db, id=id)
        self.repo.delete(db=db, id=id, soft=True)

    def get_user_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[UserSchema]:
        users = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return users

    def search_users(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[UserSchema]:
        users = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return users


users_forms_service = UserService()
