import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import text, select
from sqlalchemy.orm import Session
from config.logger import log
from crud.base import CRUDBase
from domains.auth.models.role_permissions import Role, Permission
from domains.auth.schemas.roles import (
    RolePermissionsCreate, RolePermissionsUpdate,
    PermissionCreate
)



class CRUDRole(CRUDBase[Role, RolePermissionsCreate, RolePermissionsUpdate]):
    def get_by_name(self, db: Session, *, name: str):
        result = db.execute(select(self.model).where(self.model.name == name))
        return result.scalar_one_or_none()

    def get_all(self, db: Session, *, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        query = select(self.model).offset(skip).limit(limit)
        if search:
            query = query.where(self.model.name.ilike(f"%{search}%"))
        result = db.execute(query)
        return result.scalars().all()

class CRUDPermission(CRUDBase[Permission, PermissionCreate, RolePermissionsUpdate]):
    def get_by_name(self, db: Session, *, name: str):
        result = db.execute(select(self.model).where(self.model.name == name))
        return result.scalar_one_or_none()

    def get_all(self, db: Session, *, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        query = select(self.model).offset(skip).limit(limit)
        if search:
            query = query.where(self.model.name.ilike(f"%{search}%"))
        result = db.execute(query)
        return result.scalars().all()

role_crud = CRUDRole(Role)
permission_crud = CRUDPermission(Permission)
