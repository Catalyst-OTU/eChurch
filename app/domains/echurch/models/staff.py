from db.base_class import APIBase
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Staff(APIBase):
    __table_args__ = {"schema": "public"}

    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(50), nullable=True, unique=True, index=True)

    user = relationship("User")

