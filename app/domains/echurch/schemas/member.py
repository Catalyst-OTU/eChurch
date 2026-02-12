from datetime import date
from typing import Annotated, Any, Any, List, Literal, Optional
from pydantic import BaseModel, BeforeValidator, EmailStr, UUID4
from db.schemas import BaseSchema
from utils.pydantic_validators import check_non_empty_and_not_string
from domains.echurch.schemas.centre import CentreBriefSchema
from domains.echurch.schemas.department import DepartmentBriefSchema
from domains.echurch.schemas.location import LocationBriefSchema


MemberApprovalStatus = Literal["pending", "approved", "rejected"]


class MemberBase(BaseModel):
    full_name: Annotated[str, BeforeValidator(check_non_empty_and_not_string)]
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[UUID4] = None
    user_id: Optional[UUID4] = None
    centre_id: Optional[UUID4] = None
    picture_url: Optional[str] = None
    joined_date: Optional[date] = None


class MemberCreate(MemberBase):
    approval_status: Optional[MemberApprovalStatus] = "pending"
    role_id: Optional[Any] = None
    user_id: Optional[UUID4] = None
    is_active: Optional[bool] = True


class MemberUpdate(BaseModel):
    full_name: Optional[Annotated[str, BeforeValidator(check_non_empty_and_not_string)]] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[UUID4] = None
    location_id: Optional[UUID4] = None
    centre_id: Optional[UUID4] = None
    picture_url: Optional[str] = None
    joined_date: Optional[date] = None
    approval_status: Optional[MemberApprovalStatus] = None
    is_active: Optional[bool] = None


class MemberBriefSchema(BaseSchema):
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    picture_url: Optional[str] = None


class MemberGroupInfoSchema(BaseModel):
    group_id: Optional[UUID4] = None
    group_name: Optional[str] = None
    role_department_id: Optional[UUID4] = None
    role_department_name: Optional[str] = None


class RoleSchema(BaseModel):
    id: UUID4
    name: str

class UserSchema(BaseModel):
    id: UUID4
    username: Optional[str] = None
    email: EmailStr
    is_active: bool = True
    role: Optional[RoleSchema] = None

    
class MemberSchema(MemberBase, BaseSchema):
    approval_status: MemberApprovalStatus = "pending"
    is_active: bool = True
    department: Optional[DepartmentBriefSchema] = None
    user: Optional[UserSchema] = None
    centre: Optional[CentreBriefSchema] = None


class MemberListItemSchema(MemberSchema):
    group: Optional[MemberGroupInfoSchema] = None


class MemberApprovalAction(BaseModel):
    status: MemberApprovalStatus
    reason: Optional[str] = None


class VisitorBase(BaseModel):
    full_name: Annotated[str, BeforeValidator(check_non_empty_and_not_string)]
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    location_id: Optional[UUID4] = None


class VisitorCreate(VisitorBase):
    is_active: Optional[bool] = True


class VisitorUpdate(BaseModel):
    full_name: Optional[Annotated[str, BeforeValidator(check_non_empty_and_not_string)]] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    location_id: Optional[UUID4] = None
    is_active: Optional[bool] = None


class VisitorSchema(VisitorBase, BaseSchema):
    is_active: bool = True
    location: Optional[LocationBriefSchema] = None


class RecipientSchema(BaseModel):
    id: UUID4
    recipient_type: Literal["member", "visitor"]
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None


class RecipientsResponse(BaseModel):
    data: List[RecipientSchema]

