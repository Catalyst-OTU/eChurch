from datetime import datetime
from typing import Optional, Annotated, List
from pydantic import BaseModel, EmailStr, BeforeValidator
from pydantic import UUID4
from db.schemas import BaseSchema
from utils.pydantic_validators import check_non_empty_and_not_string
from domains.auth.schemas.user_account import UserSchema

class PassengerBase(BaseModel):
    email: Annotated[EmailStr, BeforeValidator(check_non_empty_and_not_string)]
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None



class PassengerRead(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None



class PassengerCreate(PassengerBase):
    pass


class UpdatePassword(BaseModel):
    password: str


class PassengerUpdate(PassengerRead):
    pass


class PassengerInDBBase(PassengerRead, BaseSchema):
    user: Optional[UserSchema]


class PassengerSchema(PassengerInDBBase):
    pass


class RoleSchema(BaseModel):
    id: UUID4
    name: str


class BasePassenger(BaseModel):
    # organization: str
    email: Annotated[EmailStr, BeforeValidator(check_non_empty_and_not_string)]
    Passengername: Optional[str] = None
    reset_password_token: Optional[str] = None
    role_id: Optional[UUID4] = None
    is_active: bool = True
    failed_login_attempts: Optional[int] = 0
    account_locked_until: Optional[datetime] = None
    lock_count: Optional[int] = 0
    role: Optional[RoleSchema] = None


class PassengerRoleBase(BaseModel):
    # organization: str
    Passengers: List[BasePassenger]


class PassengerResponse(BaseModel):
    bk_size: int
    pg_size: int
    data: List[BasePassenger]
