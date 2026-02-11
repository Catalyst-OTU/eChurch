from typing import Any, List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.schemas.attendance import (
    AttendanceEntryCreate,
    AttendanceOverviewResponse,
    FollowUpTemplateSchema,
    FollowUpTemplateUpdate,
    MemberAttendanceItem,
)
from domains.echurch.services.attendance import attendance_service
from utils.rbac import check_if_is_system_admin, get_current_user


attendance_router = APIRouter(prefix="/attendance", responses={404: {"description": "Not found"}})


@attendance_router.post("/entries", status_code=status.HTTP_201_CREATED)
def save_attendance_entries(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    data: AttendanceEntryCreate,
) -> Any:
    return attendance_service.save_attendance_entries(db, data=data)


@attendance_router.get("/members", response_model=List[MemberAttendanceItem])
def list_member_attendance(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 100,
    search: Optional[str] = None,
) -> Any:
    return attendance_service.list_member_attendance(db, limit=limit, search=search)


@attendance_router.get("/overview", response_model=AttendanceOverviewResponse)
def get_attendance_overview(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    days: int = 365,
) -> Any:
    return attendance_service.get_overview(db, days=days)


@attendance_router.get("/templates", response_model=List[FollowUpTemplateSchema])
def get_follow_up_templates(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    return attendance_service.list_follow_up_templates(db)


@attendance_router.put("/templates/{channel}", response_model=FollowUpTemplateSchema)
def update_follow_up_template(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    channel: str,
    data: FollowUpTemplateUpdate,
) -> Any:
    return attendance_service.update_follow_up_template(db, channel=channel, data=data)

