from typing import List, Literal, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.echurch.repositories.centre import centre_repo
from domains.echurch.schemas.centre import CentreCreate, CentreSchema, CentreUpdate


class CentreService:
    def __init__(self):
        self.repo = centre_repo

    def list_centres(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: Literal["asc", "desc"] = "asc",
    ) -> List[CentreSchema]:
        return self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )

    def create_centre(self, db: Session, *, data: CentreCreate) -> CentreSchema:
        return self.repo.create(db=db, data=data)

    def update_centre(self, db: Session, *, id: UUID4, data: CentreUpdate) -> CentreSchema:
        centre = self.repo.get_by_id(db=db, id=id)
        return self.repo.update(db=db, db_obj=centre, data=data)

    def get_centre(self, db: Session, *, id: UUID4) -> CentreSchema:
        return self.repo.get_by_id(db=db, id=id)

    def delete_centre(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)


centre_service = CentreService()

