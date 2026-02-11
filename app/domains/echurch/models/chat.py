from sqlalchemy import Column, String, Integer, JSON, Date, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.base_class import APIBase
from sqlalchemy.sql import func



class ChatMessage(APIBase):
    __table_args__ = {"schema": "public"}

    trip_id = Column(UUID(as_uuid=True), ForeignKey("public.trips.id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False)
    message = Column(String, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)

    # Relationships
    trip = relationship("Trip", back_populates="chat_messages")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
