from db.base_class import APIBase
from sqlalchemy import Column, ForeignKey, Table, Text, Boolean, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
# from domains.auth.models.users import User


class UploadedFile(APIBase):
    __table_args__ = {"schema": "public"}
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    url = Column(String(255), nullable=True)
    filename = Column(String(255), nullable=True)
    type = Column(String(255),nullable=True) # profile picture, vehicle doc, etc



    user = relationship("User", back_populates="profile")
    vehicle = relationship("Vehicle", back_populates="driver")
