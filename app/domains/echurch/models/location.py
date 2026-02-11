from db.base_class import APIBase
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class Location(APIBase):
    __table_args__ = {"schema": "public"}

    name = Column(String(100), nullable=False, unique=True, index=True)

    centres = relationship("Centre", back_populates="location")
    members = relationship("Member", back_populates="location")
    visitors = relationship("Visitor", back_populates="location")

