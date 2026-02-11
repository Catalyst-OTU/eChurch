from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, UUID4

from db.schemas import BaseSchema


GivingStatus = Literal["paid", "pending", "refunded"]


class GivingTransactionBase(BaseModel):
    transaction_code: Optional[str] = None
    member_id: Optional[UUID4] = None
    payment_method: Optional[str] = None
    amount: float
    transaction_date: date
    status: Optional[GivingStatus] = "paid"
    reference: str


class GivingTransactionCreate(GivingTransactionBase):
    pass


class GivingTransactionUpdate(BaseModel):
    payment_method: Optional[str] = None
    amount: Optional[float] = None
    transaction_date: Optional[date] = None
    status: Optional[GivingStatus] = None
    reference: Optional[str] = None


class GivingTransactionSchema(GivingTransactionBase, BaseSchema):
    transaction_code: str
    member_name: Optional[str] = None
    refunded_at: Optional[datetime] = None
    refunded_by_user_id: Optional[UUID4] = None


class FinanceSummaryResponse(BaseModel):
    total_offering: float
    total_tithe: float
    total_thanksgiving: float


class RefundTransactionResponse(BaseModel):
    message: str


class AuditLogSchema(BaseSchema):
    user_id: Optional[UUID4] = None
    module: str
    action: str
    details: Optional[str] = None
