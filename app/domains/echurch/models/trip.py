from sqlalchemy import (
    Column, ForeignKey, String, Text, Float, DateTime
)
from sqlalchemy.orm import relationship
from db.base_class import APIBase
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

class Trip(APIBase):
    __table_args__ = {"schema": "public"}
    passenger_id = Column(UUID(as_uuid=True), ForeignKey("public.passengers.id"))
    driver_id = Column(UUID(as_uuid=True), ForeignKey("public.drivers.id"))
    vehicle_type = Column(String)
    pickup_location = Column(String)
    dropoff_location = Column(String)
    estimated_fare = Column(Float)
    actual_fare = Column(Float)
    payment_method = Column(String)  # 'cash', 'online'
    status = Column(String)  # 'pending', 'accepted', 'in_progress', 'completed', 'cancelled'
    started_at = Column(DateTime)
    ended_at = Column(DateTime)

    passenger = relationship("Passenger", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    cancellation = relationship("TripCancellation", back_populates="trip", uselist=False)
    chat_messages = relationship("ChatMessage", back_populates="trip", cascade="all, delete-orphan")







class TripCancellation(APIBase):
    __table_args__ = {"schema": "public"}

    trip_id = Column(UUID(as_uuid=True), ForeignKey("public.trips.id"), nullable=False, unique=True)
    cancelled_by_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False)
    reason = Column(String, nullable=True)
    cancelled_at = Column(DateTime, server_default=func.now())
    penalty_fee = Column(Float, nullable=True, default=0.0)  # optional, if any fee is charged

    trip = relationship("Trip", back_populates="cancellation")
    cancelled_by = relationship("User")


# Ensure ChatMessage is registered before mapper configuration
from .chat import ChatMessage  # noqa: E402,F401
