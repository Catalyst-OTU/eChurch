from typing import List, Literal, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.echurch.repositories.location import location_repo
from domains.echurch.schemas.location import LocationCreate, LocationSchema, LocationUpdate


class LocationService:
    def __init__(self):
        self.repo = location_repo

    def list_locations(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: Literal["asc", "desc"] = "asc",
    ) -> List[LocationSchema]:
        return self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )

    def create_location(self, db: Session, *, data: LocationCreate) -> LocationSchema:
        return self.repo.create(db=db, data=data, unique_fields=["name"])

    def update_location(self, db: Session, *, id: UUID4, data: LocationUpdate) -> LocationSchema:
        location = self.repo.get_by_id(db=db, id=id)
        return self.repo.update(db=db, db_obj=location, data=data, unique_fields=["name"])

    def get_location(self, db: Session, *, id: UUID4) -> LocationSchema:
        return self.repo.get_by_id(db=db, id=id)

    def delete_location(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)


location_service = LocationService()

