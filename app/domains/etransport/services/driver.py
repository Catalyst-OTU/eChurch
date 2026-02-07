from typing import List, Optional, Literal
from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session
from config.settings import settings
from domains.etransport.models import Driver
from domains.etransport.repositories.driver import driver_actions as driver_repo
from domains.etransport.schemas.driver import DriverSchema, DriverCreate, DriverUpdate, UserSchema
from domains.auth.services.password_reset import password_reset_service
from services.email_service import Email
from domains.auth.models.users import User
from domains.auth.respository.user_account import user_actions
from domains.auth.models.role_permissions import Role
from db.init_db import pwd_context
from domains.auth.models.refresh_token import RefreshToken

class DriverService:

    def __init__(self):
        self.repo = driver_repo



    def is_email_taken(self, db: Session, *, email: str, exclude_id: UUID4 = None, silent=True) -> bool:
        is_email_taken = self.repo.is_email_taken(db=db, email=email, exclude_id=exclude_id)
        if is_email_taken and not silent: raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already taken"
        )
        return is_email_taken

    def list_Drivers(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[DriverSchema]:
        Drivers = self.repo.get_all(
            db=db, skip=skip, limit=limit,
            order_by=order_by, order_direction=order_direction
        )
        return Drivers






    def create_Driver(self, Driver_in: DriverCreate, db: Session) -> DriverSchema:
        """Creates a new Driver under an organization and returns the Driver with role details."""
        

        check_Driver_email = user_actions.get_by_email(db, Driver_in.email)
        check_Driver_phone = driver_repo.get_user_phone(db, Driver_in.phone)

        if check_Driver_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Email already exist!')
    
        if check_Driver_phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Phone Number already exist!')

        get_Driver_role = db.query(Role).filter(Role.name == 'Driver').first()

        ##create user account for Driver
        new_user = User()
        new_user.email = Driver_in.email
        new_user.role_id = get_Driver_role.id
        new_user.password = pwd_context.hash(Driver_in.password)
        new_user.reset_password_token = None
        db.add(new_user)
        db.commit()
        db.refresh(new_user)


        ##create Driver account
        new_Driver = Driver()
        new_Driver.user_id = new_user.id
        new_Driver.full_name = Driver_in.full_name
        new_Driver.phone = Driver_in.phone
        db.add(new_Driver)
        db.commit()
        db.refresh(new_Driver)

        # email_data = send_reset_email(Driver_in.Drivername, Driver_in.email, reset_link)
        # Email.sendMailService(email_data, template_name='password_reset.html')
        return new_Driver






    def create_organization_superDriver(
            self, Driver_in: DriverCreate, db: Session, organization_access_url: str
    ) -> DriverSchema:
        """Creates a new admin Driver for an organization and send the administrator set password email."""
        #organization_service.repo.get_by_id(db=db, id=Driver_in.organization_id)
        unique_fields = ["email"]

        Driver_db = self.repo.create(db=db, data=Driver_in, unique_fields=unique_fields)

        token = password_reset_service.generate_reset_token()
        Driver_db.reset_password_token = token
        db.commit()
        #  Send email with the reset link
        reset_link = f"{organization_access_url}/login/resetpassword?token={token}"

        from domains.auth.apis.login import send_reset_email

        email_data = send_reset_email(Driver_in.Drivername, str(Driver_in.email), reset_link)
        Email.sendMailService(email_data, template_name='admin_password_reset.html')
        return Driver_db

    def update_Driver(self, db: Session, *, id: UUID4, Driver_in: DriverUpdate) -> DriverSchema:
        Driver = self.repo.get_by_id(db=db, id=id)
        Driver = self.repo.update(db=db, db_obj=Driver, data=Driver_in)
        return Driver

    def get_Driver(self, db: Session, *, id: UUID4) -> DriverSchema:
        Driver = self.repo.get_by_id(db=db, id=id)
        return Driver
    


    def get_Driver_profile_by_email(self, db: Session, *, email: str) -> UserSchema:
        Driver = user_actions.get_by_email(db, email)
        return Driver



    def block_Driver(self, db: Session, *, id: UUID4, soft_delete: bool) -> UserSchema:
        get_Driver = self.repo.get_by_id(db=db, id=id)

        get_user = user_actions.get_by_id(db=db, id=get_Driver.user_id)
        user_actions.delete(db=db, id=get_user.id, soft=soft_delete)
        return get_user




    def activate_Driver_account(self, db: Session, *, id: UUID4) -> UserSchema:
        get_Driver = self.repo.get_by_id(db=db, id=id)

        get_user = user_actions.get_by_id(db=db, id=get_Driver.user_id)
        db.query(User).filter(User.id == get_user.id).update({
            User.is_deleted: False,
            User.is_active: True
        }, synchronize_session=False)
        db.flush()
        db.commit()
        return get_user


    def delete_account_for_Driver(self, db: Session, *, id: UUID4) -> UserSchema:
        get_Driver = self.repo.get_by_id(db=db, id=id)
        #delete Driver account first
        self.repo.delete(db=db, id=id, soft=False)

        get_user = user_actions.get_by_id(db=db, id=get_Driver.user_id)

        #delete user refresh tokens second
        db.query(RefreshToken).filter(RefreshToken.user_id == get_user.id).delete()

        #delete Driver user account
        user_actions.delete(db=db, id=get_user.id, soft=False)
        return get_user
    


    def get_Driver_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[DriverSchema]:
        Drivers = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return Drivers

    def search_Drivers(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[DriverSchema]:
        Drivers = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return Drivers


drivers_service = DriverService()
