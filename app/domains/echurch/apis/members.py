from typing import Any, List, Optional

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.schemas.member import (
    MemberCreate,
    MemberListItemSchema,
    MemberSchema,
    MemberUpdate,
    VisitorCreate,
    VisitorSchema,
    VisitorUpdate,
)
from domains.echurch.services.member import member_service
from utils.rbac import check_if_is_system_admin, get_current_user


members_router = APIRouter(prefix="/members", responses={404: {"description": "Not found"}})


@members_router.get("/", response_model=List[MemberListItemSchema])
def list_members(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    approval_status: Optional[str] = None,
    department_id: Optional[UUID4] = None,
    location_id: Optional[UUID4] = None,
    centre_id: Optional[UUID4] = None,
    order_by: Optional[str] = None,
    order_direction: str = "asc",
) -> Any:
    return member_service.list_members(
        db,
        skip=skip,
        limit=limit,
        search=search,
        approval_status=approval_status,
        department_id=department_id,
        location_id=location_id,
        centre_id=centre_id,
        order_by=order_by,
        order_direction=order_direction,
    )


@members_router.post("/", response_model=MemberSchema, status_code=status.HTTP_201_CREATED)
def create_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    data: MemberCreate,
) -> Any:
    return member_service.create_member(db, data=data)


@members_router.get("/{id}", response_model=MemberSchema)
def get_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return member_service.get_member(db, id=id)


@members_router.put("/{id}", response_model=MemberSchema)
def update_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    id: UUID4,
    data: MemberUpdate,
) -> Any:
    return member_service.update_member(db, id=id, data=data)


@members_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    id: UUID4,
    soft: bool = True,
) -> None:
    member_service.delete_member(db, id=id, soft=soft)


@members_router.post("/{id}/approve", response_model=MemberSchema)
def approve_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    id: UUID4,
) -> Any:
    return member_service.set_member_approval_status(db, id=id, approval_status="approved")


@members_router.post("/{id}/reject", response_model=MemberSchema)
def reject_member(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    id: UUID4,
) -> Any:
    return member_service.set_member_approval_status(db, id=id, approval_status="rejected")


# Visitors
@members_router.get("/visitors/", response_model=List[VisitorSchema])
def list_visitors(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
) -> Any:
    return member_service.list_visitors(db, skip=skip, limit=limit, search=search)


@members_router.post("/visitors/", response_model=VisitorSchema, status_code=status.HTTP_201_CREATED)
def create_visitor(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    data: VisitorCreate,
) -> Any:
    return member_service.create_visitor(db, data=data)


@members_router.put("/visitors/{id}", response_model=VisitorSchema)
def update_visitor(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    id: UUID4,
    data: VisitorUpdate,
) -> Any:
    return member_service.update_visitor(db, id=id, data=data)


@members_router.delete("/visitors/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_visitor(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    id: UUID4,
    soft: bool = True,
) -> None:
    member_service.delete_visitor(db, id=id, soft=soft)

