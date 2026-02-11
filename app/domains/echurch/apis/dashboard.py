from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.schemas.dashboard import DashboardSummaryResponse
from domains.echurch.services.dashboard import dashboard_service
from utils.rbac import get_current_user


dashboard_router = APIRouter(prefix="/dashboard", responses={404: {"description": "Not found"}})


@dashboard_router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    return dashboard_service.get_summary(db)

