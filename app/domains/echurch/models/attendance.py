from db.base_class import APIBase
from sqlalchemy import Column, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class MemberAttendance(APIBase):
    __table_args__ = (
        UniqueConstraint(
            "member_id",
            "attendance_date",
            "service_type",
            "attendance_mode",
            name="uq_member_attendance_unique",
        ),
        {"schema": "public"},
    )

    member_id = Column(UUID(as_uuid=True), ForeignKey("public.members.id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    service_type = Column(String(50), nullable=False, index=True)  # Sunday, Wednesday, Friday
    attendance_mode = Column(String(50), nullable=True)  # In-person, Online

    member = relationship("Member", back_populates="attendances")


class FollowUpTemplate(APIBase):
    __table_args__ = (
        UniqueConstraint("channel", name="uq_follow_up_templates_channel"),
        {"schema": "public"},
    )

    channel = Column(String(50), nullable=False, index=True)  # Email, WhatsApp
    content = Column(Text, nullable=False)

