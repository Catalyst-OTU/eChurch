from datetime import date
from typing import Annotated, List, Optional

from pydantic import BaseModel, BeforeValidator, UUID4

from db.schemas import BaseSchema
from utils.pydantic_validators import check_non_empty_and_not_string

from domains.echurch.schemas.centre import CentreBriefSchema
from domains.echurch.schemas.department import DepartmentBriefSchema


class GroupBase(BaseModel):
    name: Annotated[str, BeforeValidator(check_non_empty_and_not_string)]
    centre_id: Optional[UUID4] = None
    leader_member_id: Optional[UUID4] = None
    leader_name: Optional[str] = None
    picture_url: Optional[str] = None
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[Annotated[str, BeforeValidator(check_non_empty_and_not_string)]] = None
    centre_id: Optional[UUID4] = None
    leader_member_id: Optional[UUID4] = None
    leader_name: Optional[str] = None
    picture_url: Optional[str] = None
    description: Optional[str] = None


class GroupSchema(GroupBase, BaseSchema):
    centre: Optional[CentreBriefSchema] = None


class GroupBriefSchema(BaseSchema):
    name: str


class GroupListItemSchema(GroupSchema):
    members_count: int = 0
    roles: List[str] = []


class GroupAssignMemberRequest(BaseModel):
    group_id: UUID4
    member_id: UUID4
    role_department_id: Optional[UUID4] = None
    joined_date: Optional[date] = None


class GroupMemberItemSchema(BaseModel):
    member_id: UUID4
    member_name: str
    member_phone: Optional[str] = None
    role: Optional[DepartmentBriefSchema] = None


class GroupDetailSchema(GroupSchema):
    members_count: int = 0
    roles: List[str] = []
    members: List[GroupMemberItemSchema] = []


class GroupAttendanceCreate(BaseModel):
    group_id: UUID4
    attendance_date: date
    attendance_count: int


class GroupAttendanceSchema(GroupAttendanceCreate, BaseSchema):
    pass

