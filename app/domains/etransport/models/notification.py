from db.base_class import APIBase, UUID
from sqlalchemy import Column, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship


class Notification(APIBase):
    __table_args__ = {"schema": "public"}
    user_id = Column(UUID(as_uuid=True), ForeignKey("public.users.id"))
    message = Column(String)
    is_read = Column(Boolean, default=False)

    user = relationship("User")
