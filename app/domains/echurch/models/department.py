from db.base_class import APIBase
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship


class Department(APIBase):
    __table_args__ = {"schema": "public"}

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    members = relationship("Member", back_populates="department")
    group_members = relationship("GroupMember", back_populates="role_department")

