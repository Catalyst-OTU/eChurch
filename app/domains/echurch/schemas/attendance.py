from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, UUID4

from db.schemas import BaseSchema


ServiceType = Literal["Sunday", "Wednesday", "Friday"]


class AttendanceEntryCreate(BaseModel):
    attendance_date: date
    service_type: ServiceType
    attendance_mode: Optional[str] = None  # In-person, Online
    member_ids: List[UUID4]


class MemberAttendanceItem(BaseModel):
    member_id: UUID4
    name: str
    department: Optional[str] = None
    location: Optional[str] = None
    attendance_count: int
    last_attended: Optional[date] = None


class AttendanceOverviewResponse(BaseModel):
    period: str
    total_members: int
    new_members: int
    attendance_this_period: int
    trend: List[dict]
    split: List[dict]


class FollowUpTemplateUpdate(BaseModel):
    content: str


class FollowUpTemplateSchema(BaseSchema):
    channel: str
    content: str

