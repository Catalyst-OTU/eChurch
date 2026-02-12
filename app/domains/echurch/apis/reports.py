from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.models.finance import AuditLog
from domains.echurch.schemas.reports import ExportFormat, ReportResponse, ReportType
from domains.echurch.services.reports import reports_service
from utils.rbac import get_current_user, get_current_user


reports_router = APIRouter(prefix="/reports", responses={404: {"description": "Not found"}})


@reports_router.get("/", response_model=ReportResponse)
def get_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_type: ReportType,
    report_date: Optional[date] = None,
) -> Any:
    return reports_service.generate_report(db, report_type=report_type, report_date=report_date)


@reports_router.get("/export")
def export_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    report_type: ReportType,
    report_date: Optional[date] = None,
    format: ExportFormat = "csv",
) -> Response:
    report = reports_service.generate_report(db, report_type=report_type, report_date=report_date)
    if format == "pdf":
        raise HTTPException(status_code=501, detail="PDF export not implemented yet")

    csv_text = reports_service.export_csv(report)
    db.add(AuditLog(user_id=current_user.id, module="reports", action="Exported report", details=str(report_type)))
    db.commit()
    return Response(content=csv_text, media_type="text/csv")

