from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from domains.echurch.models.attendance import FollowUpTemplate, MemberAttendance
from domains.echurch.models.department import Department
from domains.echurch.models.location import Location
from domains.echurch.models.member import Member
from domains.echurch.schemas.attendance import (
    AttendanceEntryCreate,
    AttendanceOverviewResponse,
    FollowUpTemplateSchema,
    FollowUpTemplateUpdate,
    MemberAttendanceItem,
)


class AttendanceService:
    DEFAULT_EMAIL_TEMPLATE = (
        "Hi {name}, we missed you on {date}. We hope to see you next Sunday. "
        "Reply if you need any support."
    )
    DEFAULT_WHATSAPP_TEMPLATE = (
        "Hi {name}, we missed you on {date}. We hope to see you next Sunday."
    )

    def save_attendance_entries(self, db: Session, *, data: AttendanceEntryCreate) -> dict:
        delete_query = db.query(MemberAttendance).filter(MemberAttendance.attendance_date == data.attendance_date)
        delete_query = delete_query.filter(MemberAttendance.service_type == data.service_type)
        delete_query = delete_query.filter(MemberAttendance.attendance_mode == data.attendance_mode)
        delete_query.delete(synchronize_session=False)

        for member_id in data.member_ids:
            db.add(
                MemberAttendance(
                    member_id=member_id,
                    attendance_date=data.attendance_date,
                    service_type=data.service_type,
                    attendance_mode=data.attendance_mode,
                )
            )

        db.commit()
        return {"message": "Attendance saved", "count": len(data.member_ids)}

    def list_member_attendance(self, db: Session, *, limit: int = 100, search: Optional[str] = None) -> List[MemberAttendanceItem]:
        q = (
            db.query(
                Member.id.label("member_id"),
                Member.full_name.label("name"),
                Department.name.label("department"),
                Location.name.label("location"),
                func.count(MemberAttendance.id).label("attendance_count"),
                func.max(MemberAttendance.attendance_date).label("last_attended"),
            )
            .outerjoin(MemberAttendance, MemberAttendance.member_id == Member.id)
            .outerjoin(Department, Department.id == Member.department_id)
            .outerjoin(Location, Location.id == Member.location_id)
            .filter(Member.is_deleted.is_(False))
            .filter(Member.is_active.is_(True))
            .group_by(Member.id, Department.name, Location.name)
            .order_by(func.count(MemberAttendance.id).desc())
        )

        if search:
            q = q.filter(Member.full_name.ilike(f"%{search.strip()}%"))

        rows = q.limit(limit).all()
        return [
            MemberAttendanceItem(
                member_id=row.member_id,
                name=row.name,
                department=row.department,
                location=row.location,
                attendance_count=row.attendance_count or 0,
                last_attended=row.last_attended,
            )
            for row in rows
        ]

    def get_overview(self, db: Session, *, days: int = 365) -> AttendanceOverviewResponse:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        total_members = (
            db.query(func.count(Member.id))
            .filter(Member.is_deleted.is_(False))
            .filter(Member.is_active.is_(True))
            .scalar()
            or 0
        )
        new_members = (
            db.query(func.count(Member.id))
            .filter(Member.is_deleted.is_(False))
            .filter(Member.is_active.is_(True))
            .filter(Member.created_date >= datetime.combine(start_date, datetime.min.time()))
            .scalar()
            or 0
        )

        attendance_count = (
            db.query(func.count(MemberAttendance.id))
            .filter(MemberAttendance.attendance_date >= start_date)
            .scalar()
            or 0
        )

        trend_rows = (
            db.query(
                func.date_trunc("month", MemberAttendance.attendance_date).label("month"),
                func.count(MemberAttendance.id).label("count"),
            )
            .filter(MemberAttendance.attendance_date >= start_date)
            .group_by(func.date_trunc("month", MemberAttendance.attendance_date))
            .order_by(func.date_trunc("month", MemberAttendance.attendance_date))
            .all()
        )
        trend = [{"month": row.month.strftime("%Y-%m"), "count": row.count} for row in trend_rows]

        split_rows = (
            db.query(MemberAttendance.service_type, func.count(MemberAttendance.id).label("count"))
            .filter(MemberAttendance.attendance_date >= start_date)
            .group_by(MemberAttendance.service_type)
            .order_by(func.count(MemberAttendance.id).desc())
            .all()
        )
        split = [{"service": row.service_type, "count": row.count} for row in split_rows]

        return AttendanceOverviewResponse(
            period=f"last_{days}_days",
            total_members=total_members,
            new_members=new_members,
            attendance_this_period=attendance_count,
            trend=trend,
            split=split,
        )

    def _ensure_default_templates(self, db: Session) -> None:
        existing = {t.channel.lower(): t for t in db.query(FollowUpTemplate).all()}
        to_create = []
        if "email" not in existing:
            to_create.append(FollowUpTemplate(channel="Email", content=self.DEFAULT_EMAIL_TEMPLATE))
        if "whatsapp" not in existing:
            to_create.append(FollowUpTemplate(channel="WhatsApp", content=self.DEFAULT_WHATSAPP_TEMPLATE))
        if to_create:
            db.add_all(to_create)
            db.commit()

    def list_follow_up_templates(self, db: Session) -> List[FollowUpTemplateSchema]:
        self._ensure_default_templates(db)
        templates = db.query(FollowUpTemplate).order_by(FollowUpTemplate.channel.asc()).all()
        return [FollowUpTemplateSchema.model_validate(t, from_attributes=True) for t in templates]

    def update_follow_up_template(self, db: Session, *, channel: str, data: FollowUpTemplateUpdate) -> FollowUpTemplateSchema:
        self._ensure_default_templates(db)
        template = db.query(FollowUpTemplate).filter(func.lower(FollowUpTemplate.channel) == channel.lower()).one_or_none()
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        template.content = data.content
        db.add(template)
        db.commit()
        db.refresh(template)
        return FollowUpTemplateSchema.model_validate(template, from_attributes=True)


attendance_service = AttendanceService()

