from sqlalchemy import Column, String, Integer, JSON, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.base_class import APIBase


class AdminActionLog(APIBase):
    __table_args__ = {"schema": "public"}
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    action = Column(String)
    target_user_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(String)

    admin = relationship("User", foreign_keys=[admin_user_id])
