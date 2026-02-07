from sqlalchemy import (
    Column, String, Text
)
from sqlalchemy.orm import relationship
from db.base_class import APIBase




class Vehicle(APIBase):
    __table_args__ = {"schema": "public"}
    vehicle_type = Column(String)
    registration_number = Column(String, unique=True)
    color = Column(String)
    insurance_document = Column(String)
    license_front = Column(String)
    license_back = Column(String)

    driver = relationship("Driver", back_populates="vehicle", uselist=False)
