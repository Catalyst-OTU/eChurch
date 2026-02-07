from datetime import datetime
from typing import Optional, Annotated, List
from pydantic import BaseModel, EmailStr, BeforeValidator, UUID4
from db.schemas import BaseSchema
from utils.pydantic_validators import check_non_empty_and_not_string


class UserBase(BaseModel):
    email: Annotated[EmailStr, BeforeValidator(check_non_empty_and_not_string)]
    #username: Optional[str] = None
    reset_password_token: Optional[str] = None
    role_id: Optional[UUID4] = None


class UserCreate(UserBase):
    pass


class UpdatePassword(BaseModel):
    password: str


class UserUpdate(UserBase):
    pass



class PassengerUserRead(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None



class UserInDBBase(UserBase, BaseSchema):
    is_active: bool = True
    failed_login_attempts: Optional[int] = 0
    account_locked_until: Optional[datetime] = None
    lock_count: Optional[int] = 0
    # passenger_profile: Optional[PassengerUserRead]


class UserSchema(UserInDBBase):
    pass


class RoleSchema(BaseModel):
    id: UUID4
    name: str


class BaseUser(BaseModel):
    # organization: str
    email: Annotated[EmailStr, BeforeValidator(check_non_empty_and_not_string)]
    #username: Optional[str] = None
    reset_password_token: Optional[str] = None
    role_id: Optional[UUID4] = None
    is_active: bool = True
    failed_login_attempts: Optional[int] = 0
    account_locked_until: Optional[datetime] = None
    lock_count: Optional[int] = 0
    role: Optional[RoleSchema] = None


class UserRoleBase(BaseModel):
    # organization: str
    users: List[BaseUser]


class UserResponse(BaseModel):
    bk_size: int
    pg_size: int
    data: List[BaseUser]
