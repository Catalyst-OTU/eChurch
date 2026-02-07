from datetime import datetime
from typing import Optional

from pydantic import BaseModel, UUID4


class TimestampBase(BaseModel):
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None


class BaseSchema(TimestampBase, BaseModel):
    id: Optional[UUID4] = None

    class Config:
        from_attributes = True
        validate_assignment: bool = True
        populate_by_name: bool = True
