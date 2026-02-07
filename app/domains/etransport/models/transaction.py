from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.base_class import APIBase


class Transaction(APIBase):
    __table_args__ = {"schema": "public"}
    trip_id = Column(UUID(as_uuid=True), ForeignKey("public.trips.id"))
    driver_id = Column(UUID(as_uuid=True), ForeignKey("public.drivers.id"))
    amount = Column(Float)
    service_fee = Column(Float)
    payment_method = Column(String)  # 'cash', 'online'
    status = Column(String)  # 'pending', 'paid'

    trip = relationship("Trip")
    driver = relationship("Driver")

