from typing import List, Optional, Literal

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from config.logger import log
from pydantic import UUID4
from domains.auth.models.role_permissions import Role
from domains.auth.respository.role import role_crud as role_repo
from domains.auth.schemas.roles import RolePermissionsCreate, RolePermissionsUpdate, RoleSchema


class RoleService:

    def __init__(self):
        self.repo = role_repo

    def create_role_for_organization_admin(
            self, db: Session, *, data: RolePermissionsCreate, organization_subdomain: str
    ) -> RoleSchema:
        return self.repo.create_role_for_organization_admin(
            db=db, data=data, schema_name=organization_subdomain
        )

    def create_role(self, db: Session, *, data: RolePermissionsCreate) -> RoleSchema:
        role = self.repo.create(db=db, data=data, unique_fields=["name"])
        return role

    def list_roles(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: str = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[RoleSchema]:
        """Fetch all roles under a specific organization and return them in the desired format."""

        data = role_repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
        )
        return data

    # def create_role(self, organization_id: UUID4, db: Session, *, role_in: RolePermissionsCreate) -> RoleSchema:

    #     unique_fields = ["name"]

    #     role = self.repo.create_for_tenant(db=db, data=role_in, organization_id=organization_id, unique_fields=unique_fields)
    #     return role

    # def create_role(self, schema: str, db: Session, roles: RolePermissionsCreate):
    #     tasks = []
    #     for role in roles:
    #         task = asyncio.create_task(self.repo.create_role(schema=schema, db=db, role_in=role))
    #         tasks.append(task)

    #     results = asyncio.gather(*tasks, return_exceptions=True)
    #     return results

    def update_role(self, db: Session, *, id: UUID4, data: RolePermissionsUpdate) -> RoleSchema:
        role = self.repo.update(db=db, id=id, data=data, unique_fields=["name"])
        return role

    def get_role(self, db: Session, *, id: UUID4) -> RoleSchema:
        role = self.repo.get_by_id(db=db, id=id)
        return role

    def delete_role(self, db: Session, *, id: UUID4) -> None:
        self.repo.get_by_id(db=db, id=id)
        self.repo.delete(db=db, id=id)

    def get_role_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[RoleSchema]:
        roles = self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return roles

    def search_roles(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **kwargs
    ) -> List[RoleSchema]:
        roles = self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction, **kwargs
        )
        return roles

    def get_user_role(self, db: Session, role_id, schema):
        try:
            # Convert role_id to UUID (ensure it's the correct type)
            role_id = UUID4(role_id) if isinstance(role_id, str) else role_id

            # Set schema explicitly
            db.execute(text(f'SET search_path TO "{schema}"'))
            log.debug(f"Schema switched to: {schema}")

            # Explicitly use the correct schema
            RoleSchema = Role.with_schema(schema)
            query = select(RoleSchema).where(RoleSchema.id == role_id)

            log.debug(f"Executing query in schema: {schema}")
            log.debug(str(query))
            log.debug("User role id:", role_id)

            # Execute the query
            result = db.execute(query)
            user_role = result.scalars().first()

            if user_role:
                log.debug(f"User role found: {user_role.name}")
            else:
                log.debug("User role not found.")

            return user_role

        except SQLAlchemyError as e:
            log.debug(f"Database error: {e}")
            return None


role_service = RoleService()
