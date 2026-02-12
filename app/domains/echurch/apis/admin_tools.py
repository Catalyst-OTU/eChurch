from typing import Any, List

from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.schemas.admin_tools import (
    BackupCreateRequest,
    BackupRestoreResponse,
    BackupSnapshotDetailSchema,
    BackupSnapshotSchema,
    UserRoleItem,
    UserRoleUpdateRequest,
)
from domains.echurch.services.admin_tools import admin_tools_service
from utils.rbac import get_current_user


admin_tools_router = APIRouter(prefix="/admin", responses={404: {"description": "Not found"}})


@admin_tools_router.get("/user-roles", response_model=List[UserRoleItem])
def list_user_roles(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return admin_tools_service.list_user_roles(db, skip=skip, limit=limit)


@admin_tools_router.put("/user-roles/{user_id}", response_model=UserRoleItem)
def update_user_role(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: UUID4,
    data: UserRoleUpdateRequest,
) -> Any:
    return admin_tools_service.update_user_role(db, user_id=user_id, role_id=data.role_id)


@admin_tools_router.post("/backups", response_model=BackupSnapshotSchema, status_code=status.HTTP_201_CREATED)
def create_backup(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: BackupCreateRequest,
) -> Any:
    return admin_tools_service.create_backup(db, data=data, current_user=current_user)


@admin_tools_router.get("/backups", response_model=List[BackupSnapshotSchema])
def list_backups(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return admin_tools_service.list_backups(db, skip=skip, limit=limit)


@admin_tools_router.get("/backups/{id}", response_model=BackupSnapshotDetailSchema)
def get_backup_detail(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return admin_tools_service.get_backup_detail(db, id=id)


@admin_tools_router.post("/backups/restore", response_model=BackupRestoreResponse, status_code=status.HTTP_200_OK)
def restore_backup(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
) -> Any:
    return admin_tools_service.restore_backup(db, file=file)
