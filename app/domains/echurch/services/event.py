from typing import List, Literal, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.echurch.repositories.event import church_event_repo
from domains.echurch.schemas.event import ChurchEventCreate, ChurchEventSchema, ChurchEventUpdate


class ChurchEventService:
    def __init__(self):
        self.repo = church_event_repo

    def list_events(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: Literal["asc", "desc"] = "asc",
    ) -> List[ChurchEventSchema]:
        return self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )

    def create_event(self, db: Session, *, data: ChurchEventCreate) -> ChurchEventSchema:
        return self.repo.create(db=db, data=data)

    def update_event(self, db: Session, *, id: UUID4, data: ChurchEventUpdate) -> ChurchEventSchema:
        event = self.repo.get_by_id(db=db, id=id)
        return self.repo.update(db=db, db_obj=event, data=data)

    def get_event(self, db: Session, *, id: UUID4) -> ChurchEventSchema:
        return self.repo.get_by_id(db=db, id=id)

    def delete_event(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)


church_event_service = ChurchEventService()

