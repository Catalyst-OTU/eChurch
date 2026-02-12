from typing import Any, List, Optional

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.schemas.group import (
    GroupAssignMemberRequest,
    GroupAttendanceCreate,
    GroupAttendanceSchema,
    GroupCreate,
    GroupDetailSchema,
    GroupListItemSchema,
    GroupSchema,
    GroupUpdate,
)
from domains.echurch.services.group import group_service
from utils.rbac import get_current_user, get_current_user


groups_router = APIRouter(prefix="/groups", responses={404: {"description": "Not found"}})


@groups_router.get("/", response_model=List[GroupListItemSchema])
def list_groups(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    order_by: Optional[str] = None,
    order_direction: str = "asc",
) -> Any:
    return group_service.list_groups(
        db, skip=skip, limit=limit, search=search, order_by=order_by, order_direction=order_direction
    )


@groups_router.post("/", response_model=GroupSchema, status_code=status.HTTP_201_CREATED)
def create_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: GroupCreate,
) -> Any:
    return group_service.create_group(db, data=data)


@groups_router.get("/{id}", response_model=GroupDetailSchema)
def get_group_detail(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return group_service.get_group_detail(db, id=id)


@groups_router.put("/{id}", response_model=GroupSchema)
def update_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
    data: GroupUpdate,
) -> Any:
    return group_service.update_group(db, id=id, data=data)


@groups_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> None:
    group_service.delete_group(db, id=id)


@groups_router.post("/assign-member", status_code=status.HTTP_201_CREATED)
def assign_member_to_group(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: GroupAssignMemberRequest,
) -> Any:
    group_service.assign_member(db, data=data)
    return {"message": "Member assigned"}


@groups_router.post("/attendance", response_model=GroupAttendanceSchema, status_code=status.HTTP_201_CREATED)
def record_group_attendance(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: GroupAttendanceCreate,
) -> Any:
    return group_service.record_group_attendance(db, data=data)


# Alias for Pacenta Management screens
pacentas_router = APIRouter(prefix="/pacentas", responses={404: {"description": "Not found"}})


@pacentas_router.get("/", response_model=List[GroupListItemSchema])
def list_pacentas(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
) -> Any:
    return group_service.list_groups(db, skip=skip, limit=limit, search=search)


@pacentas_router.get("/{id}", response_model=GroupDetailSchema)
def get_pacenta_detail(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return group_service.get_group_detail(db, id=id)

