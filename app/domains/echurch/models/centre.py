from db.base_class import APIBase
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Centre(APIBase):
    __table_args__ = {"schema": "public"}

    name = Column(String(150), nullable=False, index=True)
    address = Column(String(255), nullable=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("public.locations.id"), nullable=True)

    location = relationship("Location", back_populates="centres")
    groups = relationship("Group", back_populates="centre")
    members = relationship("Member", back_populates="centre")

