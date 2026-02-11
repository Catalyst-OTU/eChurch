from typing import List, Literal, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.echurch.repositories.department import department_repo
from domains.echurch.schemas.department import DepartmentCreate, DepartmentSchema, DepartmentUpdate


class DepartmentService:
    def __init__(self):
        self.repo = department_repo

    def list_departments(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_direction: Literal["asc", "desc"] = "asc",
    ) -> List[DepartmentSchema]:
        return self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )

    def create_department(self, db: Session, *, data: DepartmentCreate) -> DepartmentSchema:
        return self.repo.create(db=db, data=data, unique_fields=["name"])

    def update_department(self, db: Session, *, id: UUID4, data: DepartmentUpdate) -> DepartmentSchema:
        department = self.repo.get_by_id(db=db, id=id)
        return self.repo.update(db=db, db_obj=department, data=data, unique_fields=["name"])

    def get_department(self, db: Session, *, id: UUID4) -> DepartmentSchema:
        return self.repo.get_by_id(db=db, id=id)

    def delete_department(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)


department_service = DepartmentService()

