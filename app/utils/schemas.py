from typing import List, Optional, Union
from pydantic import BaseModel, field_validator, Field


class HTTPError(BaseModel):
    detail: str


class FileStorageSchema(BaseModel):
    filename: str
    filepath: str
    client: str


class Validators(BaseModel):
    required: Optional[bool] = False
    email: Optional[bool] = False
    unique: Optional[bool] = False
    maxLength: Optional[int] = None
    minLength: Optional[int] = None
    maximum: Optional[int] = None
    minimum: Optional[int] = None


class FormField(BaseModel):
    fieldName: str
    fieldType: str
    tooltips: Optional[str] = Field(default=None, example="A brief info or description about this fieldName")
    options: Union[str, List[str]]
    validators: Validators

    @field_validator("options")
    def validate_options(cls, v, values):
        field_type = values.data['fieldType']
        if field_type == "dropdown":
            if not isinstance(v, list) or not all(isinstance(item, str) for item in v):
                raise ValueError(
                    "options must be a list of strings for dropdown fieldType"
                )
        return v

    @field_validator("fieldName", "fieldType")
    def not_empty_or_specific_string(cls, v):
        if v == "" or v == "string":
            raise ValueError(f'{cls.__name__} field must not be empty or "string"')
        return v
