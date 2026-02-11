from typing import Any, List, Optional

from pydantic import BaseModel, UUID4

from db.schemas import BaseSchema


class UserRoleItem(BaseModel):
    user_id: UUID4
    name: str
    email: str
    role_id: Optional[UUID4] = None
    role_name: Optional[str] = None


class UserRoleUpdateRequest(BaseModel):
    role_id: UUID4


class BackupCreateRequest(BaseModel):
    notes: Optional[str] = None


class BackupSnapshotSchema(BaseSchema):
    version: str
    notes: Optional[str] = None
    created_by_user_id: Optional[UUID4] = None


class BackupSnapshotDetailSchema(BackupSnapshotSchema):
    payload: Any


class BackupRestoreResponse(BaseModel):
    message: str

