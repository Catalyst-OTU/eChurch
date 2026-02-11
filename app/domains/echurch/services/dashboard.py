from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from domains.echurch.models.attendance import MemberAttendance
from domains.echurch.models.member import Member
from domains.echurch.schemas.dashboard import DashboardCard, DashboardSummaryResponse


class DashboardService:
    def get_summary(self, db: Session, *, days: int = 365) -> DashboardSummaryResponse:
        total_members = (
            db.query(func.count(Member.id))
            .filter(Member.is_deleted.is_(False))
            .filter(Member.is_active.is_(True))
            .filter(Member.approval_status == "approved")
            .scalar()
            or 0
        )

        start_of_month = datetime(date.today().year, date.today().month, 1)
        new_members = (
            db.query(func.count(Member.id))
            .filter(Member.is_deleted.is_(False))
            .filter(Member.is_active.is_(True))
            .filter(Member.created_date >= start_of_month)
            .scalar()
            or 0
        )

        # Average Sunday attendance (last 30 days)
        start_date = date.today() - timedelta(days=30)
        sunday_rows = (
            db.query(MemberAttendance.attendance_date, func.count(MemberAttendance.id).label("count"))
            .filter(MemberAttendance.attendance_date >= start_date)
            .filter(MemberAttendance.service_type == "Sunday")
            .group_by(MemberAttendance.attendance_date)
            .all()
        )
        sunday_counts = [r.count for r in sunday_rows]
        avg_attendance = int(sum(sunday_counts) / len(sunday_counts)) if sunday_counts else 0

        cards = [
            DashboardCard(label="Total Congregation", value=int(total_members)),
            DashboardCard(label="New Members", value=int(new_members)),
            DashboardCard(label="Average Attendance", value=int(avg_attendance)),
        ]

        # Trends
        end_date = date.today()
        start_period = end_date - timedelta(days=days)

        attendance_trend_rows = (
            db.query(
                func.date_trunc("month", MemberAttendance.attendance_date).label("month"),
                func.count(MemberAttendance.id).label("count"),
            )
            .filter(MemberAttendance.attendance_date >= start_period)
            .group_by(func.date_trunc("month", MemberAttendance.attendance_date))
            .order_by(func.date_trunc("month", MemberAttendance.attendance_date))
            .all()
        )
        attendance_trend = [{"month": r.month.strftime("%Y-%m"), "count": r.count} for r in attendance_trend_rows]

        new_members_trend_rows = (
            db.query(func.date_trunc("month", Member.created_date).label("month"), func.count(Member.id).label("count"))
            .filter(Member.created_date >= datetime.combine(start_period, datetime.min.time()))
            .filter(Member.is_deleted.is_(False))
            .group_by(func.date_trunc("month", Member.created_date))
            .order_by(func.date_trunc("month", Member.created_date))
            .all()
        )
        new_members_trend = [{"month": r.month.strftime("%Y-%m"), "count": r.count} for r in new_members_trend_rows]

        return DashboardSummaryResponse(
            cards=cards,
            attendance_trend=attendance_trend,
            new_members_trend=new_members_trend,
        )


dashboard_service = DashboardService()

