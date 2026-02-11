from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, UUID4

from db.schemas import BaseSchema
from utils.pydantic_validators import check_non_empty_and_not_string

from domains.echurch.schemas.location import LocationBriefSchema


class CentreBase(BaseModel):
    name: Annotated[str, BeforeValidator(check_non_empty_and_not_string)]
    address: Optional[str] = None
    location_id: Optional[UUID4] = None


class CentreCreate(CentreBase):
    pass


class CentreUpdate(BaseModel):
    name: Optional[Annotated[str, BeforeValidator(check_non_empty_and_not_string)]] = None
    address: Optional[str] = None
    location_id: Optional[UUID4] = None


class CentreSchema(CentreBase, BaseSchema):
    location: Optional[LocationBriefSchema] = None


class CentreBriefSchema(BaseSchema):
    name: str

