from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator

from db.schemas import BaseSchema
from utils.pydantic_validators import check_non_empty_and_not_string


class DepartmentBase(BaseModel):
    name: Annotated[str, BeforeValidator(check_non_empty_and_not_string)]
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[Annotated[str, BeforeValidator(check_non_empty_and_not_string)]] = None
    description: Optional[str] = None


class DepartmentSchema(DepartmentBase, BaseSchema):
    pass


class DepartmentBriefSchema(BaseSchema):
    name: str

