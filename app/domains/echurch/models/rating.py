from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, DateTime, JSON, String, Boolean, Integer
from sqlalchemy.orm import relationship
from db.base_class import APIBase
from sqlalchemy.dialects.postgresql import UUID


class Rating(APIBase):
    __table_args__ = {"schema": "public"}
    trip_id = Column(UUID(as_uuid=True), ForeignKey("public.trips.id"))
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    rating = Column(Integer)  # 1 to 5
    comment = Column(String, nullable=True)

    trip = relationship("Trip")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
