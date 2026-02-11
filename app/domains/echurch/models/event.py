from db.base_class import APIBase
from sqlalchemy import Column, Date, String, Text, Time


class ChurchEvent(APIBase):
    __table_args__ = {"schema": "public"}

    title = Column(String(255), nullable=False, index=True)
    event_date = Column(Date, nullable=False, index=True)
    event_time = Column(Time, nullable=True)
    location = Column(String(255), nullable=True)
    event_type = Column(String(100), nullable=True, index=True)  # Service, Prayer, Conference
    status = Column(String(50), nullable=False, default="scheduled", index=True)  # scheduled/completed
    description = Column(Text, nullable=True)

