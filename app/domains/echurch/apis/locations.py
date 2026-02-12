from typing import Any, List, Literal, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from pydantic import UUID4

from domains.echurch.schemas.location import LocationCreate, LocationSchema, LocationUpdate
from domains.echurch.services.location import location_service
from utils.rbac import get_current_user, get_current_user


locations_router = APIRouter(prefix="/locations", responses={404: {"description": "Not found"}})


@locations_router.get("/", response_model=List[LocationSchema])
def list_locations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    order_by: Optional[str] = None,
    order_direction: Literal["asc", "desc"] = "asc",
) -> Any:
    return location_service.list_locations(
        db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )


@locations_router.post("/", response_model=LocationSchema, status_code=status.HTTP_201_CREATED)
def create_location(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: LocationCreate,
) -> Any:
    return location_service.create_location(db, data=data)


@locations_router.get("/{id}", response_model=LocationSchema)
def get_location(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return location_service.get_location(db, id=id)


@locations_router.put("/{id}", response_model=LocationSchema)
def update_location(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
    data: LocationUpdate,
) -> Any:
    return location_service.update_location(db, id=id, data=data)


@locations_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> None:
    location_service.delete_location(db, id=id)
