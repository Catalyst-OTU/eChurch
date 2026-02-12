from typing import Any, List, Literal, Optional

from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.schemas.event import ChurchEventCreate, ChurchEventSchema, ChurchEventUpdate
from domains.echurch.services.event import church_event_service
from utils.rbac import get_current_user, get_current_user


events_router = APIRouter(prefix="/events", responses={404: {"description": "Not found"}})


@events_router.get("/", response_model=List[ChurchEventSchema])
def list_events(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    order_by: Optional[str] = None,
    order_direction: Literal["asc", "desc"] = "asc",
) -> Any:
    return church_event_service.list_events(
        db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )


@events_router.post("/", response_model=ChurchEventSchema, status_code=status.HTTP_201_CREATED)
def create_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: ChurchEventCreate,
) -> Any:
    return church_event_service.create_event(db, data=data)


@events_router.get("/{id}", response_model=ChurchEventSchema)
def get_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> Any:
    return church_event_service.get_event(db, id=id)


@events_router.put("/{id}", response_model=ChurchEventSchema)
def update_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
    data: ChurchEventUpdate,
) -> Any:
    return church_event_service.update_event(db, id=id, data=data)


@events_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: UUID4,
) -> None:
    church_event_service.delete_event(db, id=id)

