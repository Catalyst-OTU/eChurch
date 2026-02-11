from db.base_class import APIBase
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Group(APIBase):
    __table_args__ = {"schema": "public"}

    name = Column(String(150), nullable=False, unique=True, index=True)
    centre_id = Column(UUID(as_uuid=True), ForeignKey("public.centres.id"), nullable=True)

    leader_member_id = Column(UUID(as_uuid=True), ForeignKey("public.members.id"), nullable=True)
    leader_name = Column(String(255), nullable=True)

    picture_url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)

    centre = relationship("Centre", back_populates="groups")
    leader_member = relationship("Member", foreign_keys=[leader_member_id])
    group_members = relationship("GroupMember", back_populates="group")
    attendances = relationship("GroupAttendance", back_populates="group")


class GroupMember(APIBase):
    __table_args__ = (
        UniqueConstraint("member_id", name="uq_group_members_member_id"),
        {"schema": "public"},
    )

    group_id = Column(UUID(as_uuid=True), ForeignKey("public.groups.id"), nullable=False, index=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("public.members.id"), nullable=False, index=True)
    role_department_id = Column(UUID(as_uuid=True), ForeignKey("public.departments.id"), nullable=True)
    joined_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    group = relationship("Group", back_populates="group_members")
    member = relationship("Member", back_populates="group_member")
    role_department = relationship("Department", back_populates="group_members")


class GroupAttendance(APIBase):
    __table_args__ = (
        UniqueConstraint("group_id", "attendance_date", name="uq_group_attendance_group_date"),
        {"schema": "public"},
    )

    group_id = Column(UUID(as_uuid=True), ForeignKey("public.groups.id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    attendance_count = Column(Integer, nullable=False, default=0)

    group = relationship("Group", back_populates="attendances")

