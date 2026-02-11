from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from domains.auth.models.users import User
from domains.echurch.models.finance import AuditLog, GivingTransaction
from domains.echurch.models.member import Member
from domains.echurch.repositories.finance import audit_log_repo, giving_transaction_repo
from domains.echurch.schemas.finance import (
    AuditLogSchema,
    FinanceSummaryResponse,
    GivingTransactionCreate,
    GivingTransactionSchema,
    GivingTransactionUpdate,
)


class FinanceService:
    def __init__(self):
        self.repo = giving_transaction_repo
        self.audit_repo = audit_log_repo

    def _generate_transaction_code(self, db: Session) -> str:
        base = int(datetime.utcnow().timestamp())
        for i in range(10):
            code = f"TRX-{base}{i}"
            exists = db.query(GivingTransaction).filter(GivingTransaction.transaction_code == code).count() > 0
            if not exists:
                return code
        raise HTTPException(status_code=500, detail="Could not generate transaction code")

    def list_transactions(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        reference: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> List[GivingTransactionSchema]:
        q = (
            db.query(GivingTransaction, Member.full_name.label("member_name"))
            .outerjoin(Member, Member.id == GivingTransaction.member_id)
            .filter(GivingTransaction.is_deleted.is_(False))
        )
        if reference:
            q = q.filter(func.lower(GivingTransaction.reference) == reference.lower())
        if status_filter:
            q = q.filter(func.lower(GivingTransaction.status) == status_filter.lower())
        if search:
            pattern = f"%{search.strip()}%"
            q = q.filter(
                or_(
                    GivingTransaction.transaction_code.ilike(pattern),
                    Member.full_name.ilike(pattern),
                )
            )
        rows = q.order_by(GivingTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
        items: List[GivingTransactionSchema] = []
        for tx, member_name in rows:
            schema = GivingTransactionSchema.model_validate(tx, from_attributes=True)
            schema.member_name = member_name
            items.append(schema)
        return items

    def create_transaction(self, db: Session, *, data: GivingTransactionCreate) -> GivingTransactionSchema:
        payload = data.model_dump()
        if not payload.get("transaction_code"):
            payload["transaction_code"] = self._generate_transaction_code(db)
        tx = GivingTransaction(**payload)
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return GivingTransactionSchema.model_validate(tx, from_attributes=True)

    def update_transaction(self, db: Session, *, id: UUID4, data: GivingTransactionUpdate) -> GivingTransactionSchema:
        tx = self.repo.get_by_id(db=db, id=id)
        tx = self.repo.update(db=db, db_obj=tx, data=data)
        return GivingTransactionSchema.model_validate(tx, from_attributes=True)

    def refund_transaction(self, db: Session, *, id: UUID4, current_user: User) -> GivingTransactionSchema:
        tx = self.repo.get_by_id(db=db, id=id)
        if tx.status.lower() == "refunded":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Transaction already refunded")

        tx.status = "refunded"
        tx.refunded_at = datetime.utcnow()
        tx.refunded_by_user_id = current_user.id
        db.add(tx)

        db.add(
            AuditLog(
                user_id=current_user.id,
                module="finance",
                action="Refunded transaction",
                details=f"{tx.transaction_code}",
            )
        )
        db.commit()
        db.refresh(tx)
        return GivingTransactionSchema.model_validate(tx, from_attributes=True)

    def get_summary(self, db: Session) -> FinanceSummaryResponse:
        def sum_for(ref: str) -> float:
            total = (
                db.query(func.coalesce(func.sum(GivingTransaction.amount), 0.0))
                .filter(GivingTransaction.is_deleted.is_(False))
                .filter(func.lower(GivingTransaction.reference) == ref.lower())
                .filter(func.lower(GivingTransaction.status) != "refunded")
                .scalar()
            )
            return float(total or 0.0)

        return FinanceSummaryResponse(
            total_offering=sum_for("Offering"),
            total_tithe=sum_for("Tithe"),
            total_thanksgiving=sum_for("Thanksgiving"),
        )

    def list_audit_logs(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[AuditLogSchema]:
        logs = (
            db.query(AuditLog)
            .filter(AuditLog.is_deleted.is_(False))
            .filter(AuditLog.module == "finance")
            .order_by(AuditLog.created_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [AuditLogSchema.model_validate(l, from_attributes=True) for l in logs]


finance_service = FinanceService()
