from db.base_class import APIBase
from sqlalchemy import Column, ForeignKey, Table, Text, Boolean, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
# from domains.auth.models.users import User


class Driver(APIBase):
    __table_args__ = {"schema": "public"}
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("public.vehicles.id"))
    is_verified = Column(Boolean, default=False)
    profile_picture = Column(String)
    payment_info = Column(String)
    
    user = relationship("User", back_populates="driver_profile")
    vehicle = relationship("Vehicle", back_populates="driver")
    trips = relationship("Trip", back_populates="driver")