from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator

from db.schemas import BaseSchema
from utils.pydantic_validators import check_non_empty_and_not_string


class LocationBase(BaseModel):
    name: Annotated[str, BeforeValidator(check_non_empty_and_not_string)]


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[Annotated[str, BeforeValidator(check_non_empty_and_not_string)]] = None


class LocationSchema(LocationBase, BaseSchema):
    pass


class LocationBriefSchema(BaseSchema):
    name: str

