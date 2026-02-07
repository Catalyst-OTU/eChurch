from sqlalchemy import Column, ForeignKey, JSON, Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from db.base_class import APIBase
from sqlalchemy.dialects.postgresql import UUID


class Passenger(APIBase):
    __table_args__ = {"schema": "public"}
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    full_name = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    profile_picture_url = Column(String(255), nullable=True)
    filename = Column(String(255), nullable=True)
    payment_info = Column(String(244), nullable=True)
    
    user = relationship("User", back_populates="passenger_profile")
    trips = relationship("Trip", back_populates="passenger")