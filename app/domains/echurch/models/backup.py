from db.base_class import APIBase
from sqlalchemy import Column, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class BackupSnapshot(APIBase):
    __table_args__ = {"schema": "public"}

    version = Column(String(50), nullable=False, default="1", index=True)
    notes = Column(Text, nullable=True)
    payload = Column(JSON, nullable=False)

    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=True)
    created_by = relationship("User")

