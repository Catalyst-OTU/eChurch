from typing import Any, List, Literal, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from pydantic import UUID4

from domains.echurch.schemas.department import DepartmentCreate, DepartmentSchema, DepartmentUpdate
from domains.echurch.services.department import department_service
from utils.rbac import check_if_is_system_admin, get_current_user


departments_router = APIRouter(prefix="/departments", responses={404: {"description": "Not found"}})


@departments_router.get("/", response_model=List[DepartmentSchema])
def list_departments(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    order_by: Optional[str] = None,
    order_direction: Literal["asc", "desc"] = "asc",
) -> Any:
    return department_service.list_departments(
        db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )


@departments_router.post("/", response_model=DepartmentSchema, status_code=status.HTTP_201_CREATED)
def create_department(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    data: DepartmentCreate,
) -> Any:
    return department_service.create_department(db, data=data)


@departments_router.get("/{id}", response_model=DepartmentSchema)
def get_department(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return department_service.get_department(db, id=id)


@departments_router.put("/{id}", response_model=DepartmentSchema)
def update_department(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    id: UUID4,
    data: DepartmentUpdate,
) -> Any:
    return department_service.update_department(db, id=id, data=data)


@departments_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_if_is_system_admin),
    id: UUID4,
) -> None:
    department_service.delete_department(db, id=id)
