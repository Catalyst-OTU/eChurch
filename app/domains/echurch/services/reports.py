import csv
import io
from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from domains.echurch.models.attendance import MemberAttendance
from domains.echurch.models.finance import GivingTransaction
from domains.echurch.models.member import Member
from domains.echurch.schemas.reports import ReportEntry, ReportResponse, ReportType


class ReportsService:
    def _resolve_report_date(self, db: Session, *, report_type: ReportType, report_date: Optional[date]) -> date:
        if report_date:
            return report_date

        if report_type == "financial":
            max_date = db.query(func.max(GivingTransaction.transaction_date)).scalar()
        elif report_type == "attendance":
            max_date = db.query(func.max(MemberAttendance.attendance_date)).scalar()
        else:
            max_date = db.query(func.max(func.date(Member.created_date))).scalar()

        if not max_date:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for report")
        return max_date

    def generate_report(
        self, db: Session, *, report_type: ReportType, report_date: Optional[date] = None
    ) -> ReportResponse:
        target_date = self._resolve_report_date(db, report_type=report_type, report_date=report_date)

        if report_type == "financial":
            rows = (
                db.query(GivingTransaction.reference, func.coalesce(func.sum(GivingTransaction.amount), 0.0))
                .filter(GivingTransaction.transaction_date == target_date)
                .filter(func.lower(GivingTransaction.status) != "refunded")
                .group_by(GivingTransaction.reference)
                .order_by(GivingTransaction.reference.asc())
                .all()
            )
            data = [ReportEntry(label=ref, value=float(total), date=target_date) for ref, total in rows]
            return ReportResponse(report_type=report_type, data=data)

        if report_type == "attendance":
            label_map = {
                "Sunday": "Sunday Attendance",
                "Wednesday": "Midweek Attendance",
                "Friday": "Friday Attendance",
            }
            rows = (
                db.query(MemberAttendance.service_type, func.count(MemberAttendance.id))
                .filter(MemberAttendance.attendance_date == target_date)
                .group_by(MemberAttendance.service_type)
                .order_by(func.count(MemberAttendance.id).desc())
                .all()
            )
            data = [
                ReportEntry(label=label_map.get(service, f"{service} Attendance"), value=int(count), date=target_date)
                for service, count in rows
            ]
            return ReportResponse(report_type=report_type, data=data)

        # membership
        count = (
            db.query(func.count(Member.id))
            .filter(func.date(Member.created_date) == target_date)
            .filter(Member.is_deleted.is_(False))
            .scalar()
            or 0
        )
        return ReportResponse(
            report_type=report_type,
            data=[ReportEntry(label="New Members", value=int(count), date=target_date)],
        )

    def export_csv(self, report: ReportResponse) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["label", "value", "date"])
        for row in report.data:
            writer.writerow([row.label, row.value, row.date.isoformat()])
        return output.getvalue()


reports_service = ReportsService()

