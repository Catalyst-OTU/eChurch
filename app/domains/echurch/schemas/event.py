from datetime import date, time
from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator

from db.schemas import BaseSchema
from utils.pydantic_validators import check_non_empty_and_not_string


class ChurchEventBase(BaseModel):
    title: Annotated[str, BeforeValidator(check_non_empty_and_not_string)]
    event_date: date
    event_time: Optional[time] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    status: Optional[str] = "scheduled"
    description: Optional[str] = None


class ChurchEventCreate(ChurchEventBase):
    pass


class ChurchEventUpdate(BaseModel):
    title: Optional[Annotated[str, BeforeValidator(check_non_empty_and_not_string)]] = None
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


class ChurchEventSchema(ChurchEventBase, BaseSchema):
    pass

