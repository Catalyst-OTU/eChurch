from db.base_class import APIBase
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class OutboundMessage(APIBase):
    __table_args__ = {"schema": "public"}

    channel = Column(String(50), nullable=False, index=True)  # WhatsApp, Email
    message = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="queued", index=True)
    sent_at = Column(DateTime, nullable=True)

    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=True)

    created_by = relationship("User")
    recipients = relationship("OutboundMessageRecipient", back_populates="outbound_message")


class OutboundMessageRecipient(APIBase):
    __table_args__ = {"schema": "public"}

    outbound_message_id = Column(UUID(as_uuid=True), ForeignKey("public.outbound_messages.id"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("public.members.id"), nullable=True, index=True)
    visitor_id = Column(UUID(as_uuid=True), ForeignKey("public.visitors.id"), nullable=True, index=True)

    outbound_message = relationship("OutboundMessage", back_populates="recipients")
    member = relationship("Member")
    visitor = relationship("Visitor", back_populates="message_recipients")

