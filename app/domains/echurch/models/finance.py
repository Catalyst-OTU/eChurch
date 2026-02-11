from db.base_class import APIBase
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class GivingTransaction(APIBase):
    __table_args__ = {"schema": "public"}

    transaction_code = Column(String(50), nullable=False, unique=True, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("public.members.id"), nullable=True, index=True)

    payment_method = Column(String(100), nullable=True, index=True)  # Mobile Money, Card, Bank Transfer
    amount = Column(Float, nullable=False, default=0.0)
    transaction_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="paid", index=True)  # paid/pending/refunded
    reference = Column(String(50), nullable=False, index=True)  # Offering/Tithe/Thanksgiving

    refunded_at = Column(DateTime, nullable=True)
    refunded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=True)

    member = relationship("Member", back_populates="giving_transactions")
    refunded_by = relationship("User", foreign_keys=[refunded_by_user_id])


class AuditLog(APIBase):
    __table_args__ = {"schema": "public"}

    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=True, index=True)
    module = Column(String(100), nullable=False, index=True)  # finance, reports, admin
    action = Column(String(255), nullable=False, index=True)
    details = Column(Text, nullable=True)

    user = relationship("User")

