from db.base_class import APIBase
from sqlalchemy import Boolean, Column, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Member(APIBase):
    __table_args__ = {"schema": "public"}

    full_name = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(50), nullable=True, unique=True, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)

    department_id = Column(UUID(as_uuid=True), ForeignKey("public.departments.id"), nullable=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("public.locations.id"), nullable=True)
    centre_id = Column(UUID(as_uuid=True), ForeignKey("public.centres.id"), nullable=True)

    picture_url = Column(String(512), nullable=True)
    joined_date = Column(Date, nullable=True)

    approval_status = Column(String(20), nullable=False, default="pending", index=True)
    is_active = Column(Boolean, default=True)

    department = relationship("Department", back_populates="members")
    location = relationship("Location", back_populates="members")
    centre = relationship("Centre", back_populates="members")
    # user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"), nullable=False, unique=True, index=True)

    group_member = relationship("GroupMember", back_populates="member", uselist=False)
    attendances = relationship("MemberAttendance", back_populates="member")
    giving_transactions = relationship("GivingTransaction", back_populates="member")
    user = relationship("User", back_populates="member", uselist=False)


class Visitor(APIBase):
    __table_args__ = {"schema": "public"}

    full_name = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(50), nullable=True, unique=True, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("public.locations.id"), nullable=True)

    is_active = Column(Boolean, default=True)

    location = relationship("Location", back_populates="visitors")
    message_recipients = relationship("OutboundMessageRecipient", back_populates="visitor")

