import typing as t
import uuid
from datetime import datetime, timezone
from functools import reduce
from typing import Any

import inflect
from sqlalchemy import Column, Boolean, DateTime
from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base

from utils.cls import File

Base = declarative_base(metadata=MetaData(schema=None))

class_registry: t.Dict = {}


def change_case(str):
    return reduce(lambda x, y: x + ('_' if y.isupper() else '') + y, str).lower()


class MixBase:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        camel_check = change_case(cls.__name__)
        p = inflect.engine()
        return p.plural(camel_check.lower())

    # @declared_attr
    # def __table_args__(cls):
    #     return {'schema': None} 


class BaseMethodMixin(object):
    @classmethod
    def c(cls):
        return [
            (c.name, c.type.python_type) if not isinstance(c.type, File) else (c.name, str) for c in
            cls.__table__.columns
        ]


class APIBase(BaseMethodMixin, MixBase, Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)

    def _naive_utc():
        return datetime.now(timezone.utc).replace(tzinfo=None)

    created_date = Column(DateTime, default=_naive_utc)
    updated_date = Column(DateTime, default=_naive_utc, onupdate=_naive_utc)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
