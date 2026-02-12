from typing import Any, List, Literal, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from pydantic import UUID4

from domains.echurch.schemas.centre import CentreCreate, CentreSchema, CentreUpdate
from domains.echurch.services.centre import centre_service
from utils.rbac import get_current_user, get_current_user


centres_router = APIRouter(prefix="/centres", responses={404: {"description": "Not found"}})


@centres_router.get("/", response_model=List[CentreSchema])
def list_centres(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    order_by: Optional[str] = None,
    order_direction: Literal["asc", "desc"] = "asc",
) -> Any:
    return centre_service.list_centres(db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction)


@centres_router.post("/", response_model=CentreSchema, status_code=status.HTTP_201_CREATED)
def create_centre(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: CentreCreate,
) -> Any:
    return centre_service.create_centre(db, data=data)


@centres_router.get("/{id}", response_model=CentreSchema)
def get_centre(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return centre_service.get_centre(db, id=id)


@centres_router.put("/{id}", response_model=CentreSchema)
def update_centre(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
    data: CentreUpdate,
) -> Any:
    return centre_service.update_centre(db, id=id, data=data)


@centres_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_centre(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> None:
    centre_service.delete_centre(db, id=id)
