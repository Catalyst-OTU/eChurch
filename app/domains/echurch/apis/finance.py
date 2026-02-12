from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.models.finance import AuditLog
from domains.echurch.schemas.finance import (
    AuditLogSchema,
    FinanceSummaryResponse,
    GivingTransactionCreate,
    GivingTransactionSchema,
    GivingTransactionUpdate,
)
from domains.echurch.services.finance import finance_service
from utils.rbac import get_current_user, get_current_user


finance_router = APIRouter(prefix="/finance", responses={404: {"description": "Not found"}})


@finance_router.get("/summary", response_model=FinanceSummaryResponse)
def get_finance_summary(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    return finance_service.get_summary(db)


@finance_router.get("/transactions", response_model=List[GivingTransactionSchema])
def list_transactions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    reference: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> Any:
    return finance_service.list_transactions(
        db, skip=skip, limit=limit, search=search, reference=reference, status_filter=status_filter
    )


@finance_router.post("/transactions", response_model=GivingTransactionSchema, status_code=status.HTTP_201_CREATED)
def create_transaction(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: GivingTransactionCreate,
) -> Any:
    return finance_service.create_transaction(db, data=data)


@finance_router.put("/transactions/{id}", response_model=GivingTransactionSchema)
def update_transaction(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
    data: GivingTransactionUpdate,
) -> Any:
    return finance_service.update_transaction(db, id=id, data=data)


@finance_router.post("/transactions/{id}/refund", response_model=GivingTransactionSchema)
def refund_transaction(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return finance_service.refund_transaction(db, id=id, current_user=current_user)


@finance_router.get("/audit-logs", response_model=List[AuditLogSchema])
def list_finance_audit_logs(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return finance_service.list_audit_logs(db, skip=skip, limit=limit)


@finance_router.get("/export")
def export_transactions_csv(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    reference: Optional[str] = None,
) -> Response:
    transactions = finance_service.list_transactions(db, skip=0, limit=10000, reference=reference)
    lines = ["transaction_code,member_name,amount,reference,status,transaction_date,payment_method"]
    for tx in transactions:
        lines.append(
            f"{tx.transaction_code},{tx.member_name or ''},{tx.amount},{tx.reference},{tx.status},{tx.transaction_date},{tx.payment_method or ''}"
        )

    db.add(AuditLog(user_id=current_user.id, module="finance", action="Exported report", details="transactions"))
    db.commit()

    content = "\n".join(lines)
    return Response(content=content, media_type="text/csv")

