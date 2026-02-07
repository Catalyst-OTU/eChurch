import re
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator, UUID4
from db.schemas import BaseSchema


class Role(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="The name of the role.")

    @validator("name")
    def name_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Role name cannot be empty or just whitespace.")
        return value.strip()

    @validator("name")
    def name_must_be_alphanumeric_with_spaces(cls, value):
        if not re.match(r"^[a-zA-Z0-9\s]+$", value):
            raise ValueError("Role name must contain only alphanumeric characters and spaces.")
        return value


class RolePermissionsCreate(Role):
    permissions: Optional[Union[str, List[str]]] = Field(
        None,
        description="List of permission names to assign to the role."
    )

    @validator("permissions")
    def permissions_must_be_valid(cls, value):
        if isinstance(value, str):
            return [value.strip()]
        elif isinstance(value, list):
            return [perm.strip() for perm in value if
                    perm and isinstance(perm, str)]  # Strip and filter empty/non-string permissions
        return None


class RolePermissionsCreate(Role):
    permissions_ids: Optional[List[UUID4]] = Field(None, description="List of permission IDs to assign to the role.")


class RolePermissionsUpdate(Role):
    new_permission_ids: Optional[List[UUID4]] = Field(
        None,
        description="List of new permission IDs to assign to the role (optional)."
    )


class PermissionResponse(BaseSchema):
    name: str = Field(..., description="The name of the permission.")


class RoleResponse(BaseSchema):
    name: str = Field(..., description="The name of the role.")
    permissions: List[PermissionResponse] = Field(
        default_factory=list,
        description="List of permission names and IDs associated with the role."
    )


class RoleResponse(BaseSchema):
    name: str = Field(..., description="The name of the role.")
    permissions: List[str] = Field(..., description="List of permission names associated with the role.")


class PermissionName(BaseModel):
    name: str = Field(..., description="The name of the permission.")

    # name: str = Field(..., min_length=1, max_length=100, description="The name of the permission.")

    @validator("name")
    def name_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Permission name cannot be empty or just whitespace.")
        return value.strip()

    @validator("name")
    def name_must_be_alphanumeric_with_spaces(cls, value):
        if not re.match(r"^[a-zA-Z0-9\s:]+$", value):
            raise ValueError("Permission name must contain only alphanumeric characters, colons and spaces.")
        return value


class Permission(BaseModel):
    id: UUID4 = Field(..., description="The ID of the permission.")


class PermissionCreate(PermissionName):
    pass


class PermissionUpdate(PermissionName):
    pass


class ShowPermission(BaseSchema):
    name: str = Field(..., description="The name of the permission.")


class RoleInDBBase(BaseSchema):
    name: str = Field(min_length=1, max_length=50, example="admin")


class RoleSchema(RoleInDBBase):
    pass
