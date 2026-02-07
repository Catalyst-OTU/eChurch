from typing import List, Optional, Literal
from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session
from config.settings import settings
from domains.etransport.models import Passenger
from domains.etransport.repositories.passenger import passenger_actions as passenger_repo
from domains.etransport.schemas.passenger import PassengerSchema, PassengerCreate, PassengerUpdate, UserSchema
from domains.auth.services.password_reset import password_reset_service
from services.email_service import Email
from domains.auth.models.users import User
from domains.auth.respository.user_account import user_actions
from domains.auth.models.role_permissions import Role
from db.init_db import pwd_context
from domains.auth.models.refresh_token import RefreshToken

class PassengerService:

    def __init__(self):
        self.repo = passenger_repo



    def is_email_taken(self, db: Session, *, email: str, exclude_id: UUID4 = None, silent=True) -> bool:
        is_email_taken = self.repo.is_email_taken(db=db, email=email, exclude_id=exclude_id)
        if is_email_taken and not silent: raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already taken"
        )
        return is_email_taken

    def list_Passengers(
            self,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[PassengerSchema]:
        Passengers = self.repo.get_all(
            db=db, skip=skip, limit=limit,
            order_by=order_by, order_direction=order_direction
        )
        return Passengers






    def create_Passenger(self, Passenger_in: PassengerCreate, db: Session) -> PassengerSchema:
        """Creates a new Passenger under an organization and returns the Passenger with role details."""
        

        check_passenger_email = user_actions.get_by_email(db, Passenger_in.email)
        check_passenger_phone = passenger_repo.get_user_phone(db, Passenger_in.phone)

        if check_passenger_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Email already exist!')
    
        if check_passenger_phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Phone Number already exist!')

        get_passenger_role = db.query(Role).filter(Role.name == 'Passenger').first()

        ##create user account for passenger
        new_user = User()
        new_user.email = Passenger_in.email
        new_user.role_id = get_passenger_role.id
        new_user.password = pwd_context.hash(Passenger_in.password)
        new_user.reset_password_token = None
        db.add(new_user)
        db.commit()
        db.refresh(new_user)


        ##create passenger account
        new_Passenger = Passenger()
        new_Passenger.user_id = new_user.id
        new_Passenger.full_name = Passenger_in.full_name
        new_Passenger.phone = Passenger_in.phone
        db.add(new_Passenger)
        db.commit()
        db.refresh(new_Passenger)

        # email_data = send_reset_email(Passenger_in.Passengername, Passenger_in.email, reset_link)
        # Email.sendMailService(email_data, template_name='password_reset.html')
        return new_Passenger






    def create_organization_superPassenger(
            self, Passenger_in: PassengerCreate, db: Session, organization_access_url: str
    ) -> PassengerSchema:
        """Creates a new admin Passenger for an organization and send the administrator set password email."""
        #organization_service.repo.get_by_id(db=db, id=Passenger_in.organization_id)
        unique_fields = ["email"]

        Passenger_db = self.repo.create(db=db, data=Passenger_in, unique_fields=unique_fields)

        token = password_reset_service.generate_reset_token()
        Passenger_db.reset_password_token = token
        db.commit()
        #  Send email with the reset link
        reset_link = f"{organization_access_url}/login/resetpassword?token={token}"

        from domains.auth.apis.login import send_reset_email

        email_data = send_reset_email(Passenger_in.Passengername, str(Passenger_in.email), reset_link)
        Email.sendMailService(email_data, template_name='admin_password_reset.html')
        return Passenger_db

    def update_Passenger(self, db: Session, *, id: UUID4, Passenger_in: PassengerUpdate) -> PassengerSchema:
        Passenger = self.repo.get_by_id(db=db, id=id)
        Passenger = self.repo.update(db=db, db_obj=Passenger, data=Passenger_in)
        return Passenger

    def get_Passenger(self, db: Session, *, id: UUID4) -> PassengerSchema:
        Passenger = self.repo.get_by_id(db=db, id=id)
        return Passenger
    


    def get_Passenger_profile_by_email(self, db: Session, *, email: str) -> UserSchema:
        Passenger = user_actions.get_by_email(db, email)
        return Passenger



    def block_Passenger(self, db: Session, *, id: UUID4, soft_delete: bool) -> UserSchema:
        get_passenger = self.repo.get_by_id(db=db, id=id)

        get_user = user_actions.get_by_id(db=db, id=get_passenger.user_id)
        user_actions.delete(db=db, id=get_user.id, soft=soft_delete)
        return get_user




    def activate_passenger_account(self, db: Session, *, id: UUID4) -> UserSchema:
        get_passenger = self.repo.get_by_id(db=db, id=id)

        get_user = user_actions.get_by_id(db=db, id=get_passenger.user_id)
        db.query(User).filter(User.id == get_user.id).update({
            User.is_deleted: False,
            User.is_active: True
        }, synchronize_session=False)
        db.flush()
        db.commit()
        return get_user


    def delete_account_for_passenger(self, db: Session, *, id: UUID4) -> UserSchema:
        get_passenger = self.repo.get_by_id(db=db, id=id)
        #delete passenger account first
        self.repo.delete(db=db, id=id, soft=False)

        get_user = user_actions.get_by_id(db=db, id=get_passenger.user_id)

        #delete user refresh tokens second
        db.query(RefreshToken).filter(RefreshToken.user_id == get_user.id).delete()

        #delete passenger user account
        user_actions.delete(db=db, id=get_user.id, soft=False)
        return get_user
    


    def get_Passenger_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[PassengerSchema]:
        Passengers = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return Passengers

    def search_Passengers(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[PassengerSchema]:
        Passengers = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return Passengers


passengers_service = PassengerService()
