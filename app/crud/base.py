from datetime import datetime
from typing import (
    Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Literal, Sequence, Tuple
)
from uuid import UUID

from fastapi import HTTPException, Request
from pydantic import BaseModel, UUID4
from sqlalchemy import or_, desc, select, delete, text, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound
from sqlalchemy.orm import selectinload, joinedload, Session
from sqlalchemy.orm.relationships import RelationshipProperty
from starlette import status
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from config.logger import log
from db.base_class import APIBase
from db.session import engine
from utils.exceptions import http_500_exc_internal_server_error

ModelType = TypeVar("ModelType", bound=APIBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations on database models.

    Provides common database operations with error handling and type safety.

    Type Parameters:
        ModelType: The SQLAlchemy model type
        CreateSchemaType: Pydantic model for creation operations
        UpdateSchemaType: Pydantic model for update operations
    """

    def __init__(self, model: Type[ModelType], select_related: Tuple = None):
        """
        Initialize the repository with a specific model.

        Args:
            model: SQLAlchemy model class
            select_related: Tuple of SQLAlchemy model related columns
        """
        self.model = model
        self.query = select(self.model)
        if select_related is not None:
            fields_to_select = (selectinload(field) for field in select_related)
            self.query = select(self.model).options(*fields_to_select)

    def get_by_subdomain(self, db: Session, *, subdomain: str, silent=True):
        """
        Retrieve a single record by its domain name.
        """
        try:
            organization = db.query(self.model).filter(self.model.subdomain == subdomain).one_or_none()

            if not organization:
                if silent:
                    return None
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Organization not found for {subdomain}",
                )

            if not organization.is_active and silent:
                return None

            return organization
        except Exception:
            log.exception(f"Error in get_by_subdomain for {self.model.__name__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    def get_settings_by_subdomain(self, db: Session, *, subdomain: str, organization_id: any):
        """
        Retrieve settings by subdomain.
        """
        try:
            schema = subdomain
            query = f'SELECT * FROM "{schema}".organization_setting'
            params = {}
            if organization_id:
                query += ' WHERE organization_id = :organization_id'
                params["organization_id"] = organization_id

            result = db.execute(text(query), params)
            row = result.mappings().one_or_none()
            return dict(row) if row else None
        except NoResultFound:
            return None
        except Exception:
            log.exception(f"Error in get_settings_by_subdomain for {self.model.__name__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    def get_by_id(self, db: Session, *, id: any, silent=False):
        """
        Retrieve a single record by its ID.
        """
        if id is None:
            return None
        try:
            return db.query(self.model).filter(self.model.id == id).one()
        except NoResultFound:
            if silent:
                return None
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )
        except SQLAlchemyError:
            log.error(f"Database error fetching {self.model.__name__} with id={id}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
            )
        except Exception:
            log.exception(f"Unexpected error fetching {self.model.__name__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    def get_by_field(self, db: Session, *, field: str, value: any, silent=False):
        """
        Retrieve a single record by matching a specific field value.
        """
        if value is None:
            return None
        try:
            return db.query(self.model).filter(getattr(self.model, field) == value).one()
        except NoResultFound:
            if silent:
                return None
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )
        except AttributeError:
            log.error(f"Invalid field {field} for model {self.model.__name__}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid field: {field}"
            )
        except Exception:
            log.exception(f"Error in get_by_field for {self.model.__name__}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


    def get_many_by_ids(self, db: Session, *, ids: list, silent=False):
        """
        Retrieve multiple records by their IDs.
        """
        if not ids:
            return []

        # Normalize to UUIDs
        try:
            ids = [UUID(str(id_)) for id_ in ids]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid UUID in list: {e}")

        try:
            found_objects = db.query(self.model).filter(self.model.id.in_(ids)).all()
            missing_ids = set(ids) - {obj.id for obj in found_objects}
            if missing_ids and not silent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Records not found for ids: {missing_ids}",
                )
            return found_objects
        except Exception:
            log.exception(f"Error in get_many_by_ids for {self.model.__name__}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found")


    def get_all(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> Sequence[ModelType]:
        try:
            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = self.query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )
            else:
                query = self.query.order_by(desc(self.model.created_date))

            query = query.offset(skip).limit(limit)
            result = db.execute(query)
            return result.scalars().all()
        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {self.model.__name__}", exc_info=True)
            return []
        except:
            log.exception(f"Unexpected error in get_all {self.model.__name__}")
            raise http_500_exc_internal_server_error()

    def get_by_filters(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **filters: Any
    ) -> Sequence[ModelType]:
        query = self.query
        try:
            for field, value in filters.items():
                if value is not None:
                    query = query.filter(getattr(self.model, field) == value)

            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )

            query = query.offset(skip).limit(limit)
            result = db.execute(query)
            return result.scalars().all()

        except HTTPException:
            raise
        except AttributeError as e:
            log.error("Invalid filter field")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f'Invalid filter field provided for {self.model.__name__}'
            )
        except:
            log.exception(f"Error in get_by_filters for {self.model.__name__}")
            raise http_500_exc_internal_server_error()

    def get_by_pattern(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **patterns: Any
    ) -> Sequence[ModelType]:
        query = self.query
        try:
            for field, pattern in patterns.items():
                if not pattern:
                    continue
                field_attr = getattr(self.model, field)
                if isinstance(pattern, list):
                    valid_patterns = [p for p in pattern if p]
                    if valid_patterns:
                        query = query.filter(or_(*[field_attr.ilike(f"%{p}%") for p in valid_patterns]))
                    else:
                        continue
                else:
                    query = query.filter(field_attr.ilike(f"%{pattern}%"))

            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )

            query = query.offset(skip).limit(limit)
            result = db.execute(query)
            return result.scalars().all()

        except HTTPException:
            raise
        except AttributeError as e:
            log.error("Invalid pattern matching field", exc_info=True)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=f'Invalid field for pattern matching: {str(e)}'
            )
        except:
            log.exception(f"Error in get_by_pattern for {self.model.__name__}")
            raise http_500_exc_internal_server_error()

    def get_or_create(
            self, *,
            db: Session,
            data: CreateSchemaType,
            unique_field: str,
    ) -> ModelType:
        try:
            result = db.execute(
                self.query.filter(getattr(self.model, unique_field) == getattr(data, unique_field))
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing

            return self.create(db=db, data=data)

        except HTTPException:
            db.rollback()
            raise
        except:
            log.exception(f"Error in get_or_create for {self.model.__name__}")
            db.rollback()
            raise http_500_exc_internal_server_error()

    def create(self, db: Session, *, data: CreateSchemaType, unique_fields: list = None) -> ModelType:
        if unique_fields is None:
            unique_fields = []
        if not data:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="No data provided for creation"
            )

        try:
            # model_data = data.model_dump(exclude_none=True, exclude_defaults=False)
            if isinstance(data, BaseModel):
                model_data = data.model_dump(exclude_none=True, exclude_defaults=False)
            else:
                # fallback for dicts
                model_data = {k: v for k, v in data.items() if v is not None}

            self.validate_unique_fields(db=db, model_data=model_data, unique_fields=unique_fields)

            db_obj = self.model(**model_data)
            db.add(db_obj)
            db.commit()
            return self.get_by_id(db=db, id=db_obj.id)

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            log.error(f"Integrity error creating {self.model.__name__}", exc_info=True)
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=self._format_integrity_error(e))

    def update(
            self, *,
            db: Session,
            data: Union[UpdateSchemaType, Dict[str, Any]],
            db_obj: Optional[ModelType] = None,
            id: Optional[UUID4] = None,
            unique_fields: Optional[List] = None
    ) -> ModelType:
        if unique_fields is None:
            unique_fields = []

        if not db_obj and not id:
            raise HTTPException(status_code=400, detail="Either the db_obj or id must be provided for update")

        if not db_obj:
            db_obj = self.get_by_id(db=db, id=id)

        if not db_obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")

        try:
            update_data = data.model_dump(exclude_none=True) if isinstance(data, BaseModel) else data
            self.validate_unique_fields(db=db, model_data=update_data, unique_fields=unique_fields, id=id)

            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            log.exception(f"Error updating {self.model.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during update")

    def delete(self, db: Session, *, id: UUID4, soft: bool = False) -> None:
        """
        Delete a record by ID.

        Args:
            db: Database session
            id: Record ID to delete
            soft: argument to either soft delete the record or not

        Raises:
            HTTPException: 404 if not found, 409 if deletion violates constraints
        """
        # Check existence
        existing_obj = self.get_by_id(db=db, id=id)
        try:
            if soft:
                existing_obj.is_deleted = True
                existing_obj.is_active = False
                existing_obj.deleted_at = datetime.utcnow()

                # Mark the object as changed
                db.add(existing_obj)
                db.commit()
            else:
                # Perform hard deletion
                db.execute(
                    delete(self.model)
                    .where(self.model.id == id)
                    .execution_options(synchronize_session=False)
                )
                db.commit()

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError:
            db.rollback()
            log.error(f"Integrity error deleting {self.model.__name__}", exc_info=True)
        except:
            db.rollback()
            log.exception(f"Error deleting {self.model.__name__}")
            raise http_500_exc_internal_server_error()

    def bulk_hard_delete(self, db: Session, *, ids: List[UUID4]) -> None:
        """
        Delete multiple records by ID.

        Args:
            db: Database session
            ids: List of record IDs to delete

        Raises:
            HTTPException: 404 if not found, 409 if deletion violates constraints
        """
        if not ids: return
        try:
            result = db.execute(delete(self.model).where(self.model.id.in_(ids)))
            db.commit()

            # Check if all rows were deleted
            if result.rowcount != len(ids):
                log.warning(f"Requested to delete {len(ids)} records, but only {result.rowcount} were deleted")

        except HTTPException:
            db.rollback()
            log.exception("failed to delete")
            raise
        except IntegrityError:
            db.rollback()
            log.error(f"Integrity error during bulk delete of {self.model.__name__}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot delete some {self.model.__name__} records due to constraints"
            )
        except Exception:
            db.rollback()
            log.exception(f"Error during bulk delete of {self.model.__name__}")
            raise http_500_exc_internal_server_error()

    def reactivate(self, db: Session, *, id: UUID4) -> None:
        """Reactivates a soft-deleted record by setting is_deleted to False and is_active to True."""
        existing_obj = self.get_by_id(db, id=id, silent=False)
        try:
            existing_obj.is_deleted = False
            existing_obj.is_active = True
            existing_obj.deleted_at = None

            # Mark the object as changed
            db.add(existing_obj)
            db.commit()

        except HTTPException:
            db.rollback()
            raise
        except:
            db.rollback()
            log.exception(f"Failed to reactivate {self.model.__name__}")
            raise http_500_exc_internal_server_error()

    @staticmethod
    def _format_integrity_error(e: IntegrityError) -> str:
        """Prettifies SQLAlchemy IntegrityError messages."""
        error_message = str(e.orig)

        if isinstance(e.orig, Exception):
            if "ForeignKeyViolationError" in error_message:
                start = error_message.find("Key (")
                if start != -1:
                    detail = error_message[start:].replace("DETAIL: ", "").strip()
                    return f"Foreign key constraint violated: {detail}"
                return "Foreign key constraint violated."
            elif "UniqueViolationError" in error_message:
                return "Unique constraint violated. A similar record already exists."

        return str(e.orig)

    def validate_unique_fields(self, db: Session, *, model_data: dict, unique_fields: List, id: UUID = None):
        for field in unique_fields:
            if field in model_data and model_data[field]:
                query = select(self.model).where(getattr(self.model, field) == model_data[field])

                if id:
                    if not isinstance(id, UUID):
                        raise HTTPException(status_code=400, detail="Invalid UUID format for ID")
                    query = query.where(self.model.id != id)

                result = db.execute(query)
                if result.scalars().first():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"'{field}' for {model_data[field]} already exists"
                    )

    def get_related_model(self, use_related_name: str):
        relation = getattr(self.model, use_related_name)
        if not isinstance(relation.prop, RelationshipProperty):
            raise AttributeError(f"{use_related_name} is not a valid relation")
        return relation, relation.prop.mapper.class_

    def _base(
            self,
            db: Session,
            fields=None,
            use_related_name: str = None,
            resource_id: int = None,
            joins: dict = {}
    ):
        if use_related_name and resource_id:
            relation, related_model = self.get_related_model(use_related_name)
            b_fields = [getattr(related_model, field.strip()) for field in fields] if fields else [related_model]
            base = select(*b_fields).join(related_model, relation).where(self.model.id == resource_id)
            model = related_model
        else:
            b_fields = [getattr(self.model, field.strip()) for field in fields] if fields else [self.model]
            base = select(*b_fields)
            model = self.model

        if joins:
            target = self.model
            filters_dict = joins.get('filters', {})
            join_list = joins.get('joins', [])

            base = base.where(
                *[getattr(target, key) == value for key, value in filters_dict.items() if hasattr(target, key)])

            for join in join_list:
                relation_name = join.get('relation_name')
                join_filters = join.get('filters', {})

                if relation_name:
                    base = base.options(joinedload(getattr(target, relation_name)))
                    base = base.join(getattr(target, relation_name)).where(
                        *[getattr(join['target'], key) == value for key, value in join_filters.items() if
                          hasattr(join['target'], key)]
                    )

            model = target

        return model, base

    def special_read(
            self,
            request: Request,
            db: Session,
            use_related_name: str = None,
            resource_id: int = None,
            joins: dict = {},
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ):
        try:
            params = {
                k: v for k, v in request.query_params.items()
                if k in ['offset', 'limit', 'fields', 'q', 'sort'] or any(k == col[0] for col in self.model.c())
            }

            model_to_filter, base = self._base(
                db,
                params.get('fields', None),
                use_related_name=use_related_name,
                resource_id=resource_id,
                joins=joins
            )

            # Convert 'id' filter to UUID
            filters = {}
            for key, value in request.query_params.items():
                if hasattr(model_to_filter, key):
                    if key == "id":  # Ensure correct filtering for UUID type
                        try:
                            filters[key] = UUID(value)
                        except ValueError:
                            raise HTTPException(status_code=400, detail=f"Invalid UUID format for {key}: {value}")
                    else:
                        filters[key] = value

            # Apply query parameter filters
            base = base.where(*[getattr(model_to_filter, key) == value for key, value in filters.items()])

            if order_by:
                order_field = getattr(model_to_filter, order_by, None)
                if not order_field:
                    raise ValueError(f"Invalid order_by column: {order_by}")
                base = base.order_by(order_field.asc() if order_direction == 'asc' else order_field.desc())
            elif params.get('sort'):
                if isinstance(params['sort'], str):
                    params['sort'] = [params['sort']]
                sort_expressions = []
                for key in params['sort']:
                    field_name = key[1:] if key.startswith('-') else key
                    order_field = getattr(model_to_filter, field_name, None)
                    if order_field is None:
                        raise ValueError(f"Invalid sort field: {field_name}")
                    sort_expressions.append(order_field.desc() if key.startswith('-') else order_field.asc())
                base = base.order_by(*sort_expressions)

            data_stmt = base.offset(int(params.get('offset', 0))).limit(int(params.get('limit', 100)))
            data_result = db.execute(data_stmt)
            data = data_result.unique().scalars().all()
            count_stmt = base.with_only_columns(func.count('*')).order_by(None)
            count_result = db.execute(count_stmt)
            bk_size = count_result.scalar() or 0

            return {
                'bk_size': bk_size,
                'pg_size': len(data),
                'data': data
            }
        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {self.model.__name__}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found.")
        except:
            log.exception(f"Unexpected error in get_all {self.model.__name__}")
            raise http_500_exc_internal_server_error()

    def create_schema(self, *, subdomain: str, db: Session):
        """Creates a new database schema dynamically."""
        # appraisal imports
        from domains.appraisal.models.appraisal import Appraisal
        from domains.appraisal.models.appraisal_comment import AppraisalComment, appraisal_submission_comments
        from domains.appraisal.models.appraisal_input import AppraisalInput
        from domains.appraisal.models.appraisal_submission import AppraisalSubmission
        from domains.appraisal.models.appraisal_template import AppraisalTemplate
        from domains.appraisal.models.department_group import DepartmentGroup
        from domains.appraisal.models.appraisal_cycle import AppraisalCycle
        from domains.appraisal.models.appraisal_section import AppraisalSection
        from domains.organization.models.organization_staff_role_permissions import (
            OrganizationRole, OrganizationPermission,
            organization_role_permissions, organization_staff_permissions, Staff, StaffSupervisor
        )

        # organization imports
        from domains.organization.models.form_template import FormFieldTemplate
        from domains.organization.models.organization_branch import OrganizationBranch
        from domains.organization.models.department import Department, HeadOfDepartment, HeadOfDepartmentUnit, \
            DepartmentUnit
        # from domains.organization.models.staff import Staff, StaffSupervisor

        # tenancy imports
        from domains.tenancies.models.terms_and_conditions import TermsAndConditions
        from domains.tenancies.models.tenancy import Tenancy
        from domains.tenancies.models.bill import Bill
        from domains.tenancies.models.payment import Payment

        # Create schema
        db.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{subdomain}"'))
        db.commit()

        # Assign schema to tables
        Staff.__table__.schema = subdomain
        StaffSupervisor.__table__.schema = subdomain
        Department.__table__.schema = subdomain
        HeadOfDepartment.__table__.schema = subdomain
        DepartmentUnit.__table__.schema = subdomain
        HeadOfDepartmentUnit.__table__.schema = subdomain
        Appraisal.__table__.schema = subdomain
        AppraisalComment.__table__.schema = subdomain
        AppraisalInput.__table__.schema = subdomain
        AppraisalSubmission.__table__.schema = subdomain
        AppraisalTemplate.__table__.schema = subdomain
        AppraisalCycle.__table__.schema = subdomain
        AppraisalSection.__table__.schema = subdomain
        DepartmentGroup.__table__.schema = subdomain
        FormFieldTemplate.__table__.schema = subdomain
        OrganizationRole.__table__.schema = subdomain
        OrganizationPermission.__table__.schema = subdomain
        organization_role_permissions.schema = subdomain
        organization_staff_permissions.schema = subdomain
        OrganizationBranch.__table__.schema = subdomain
        appraisal_submission_comments.schema = subdomain
        TermsAndConditions.__table__.schema = subdomain
        Tenancy.__table__.schema = subdomain
        Bill.__table__.schema = subdomain
        Payment.__table__.schema = subdomain

        # Create tables synchronously
        with engine.begin() as conn:
            APIBase.metadata.create_all(conn)
