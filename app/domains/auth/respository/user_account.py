from typing import Dict, Any, Union, Optional
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.orm import Session
from crud.base import CRUDBase, ModelType
from domains.auth.models.users import User
from domains.auth.schemas.user_account import (
    UserCreate, UserUpdate
)
from utils.security import pwd_context


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def is_email_taken(self, db: Session, email: str, exclude_id: UUID4) -> bool:
        if not email: return True
        query = db.query(User).filter(User.email == email)
        if exclude_id: query = query.filter(User.id != exclude_id)
        return query.count() > 0

    # def get_by_email(self, db: Session, *, email: Any, silent=False) -> Optional[ModelType]:
    #     if not email: return None
    #     return self.get_by_field(db=db, field="email", value=email, silent=silent)


    def get_by_email(self, db: Session, email: str):
        return db.query(self.model).filter(self.model.email == email.strip()).first()


    def get_by_reset_password_token(self, db: Session, token: Any) -> Optional[ModelType]:
        if not token: return None
        return self.get_by_field(db=db, field="reset_password_token", value=token, silent=True)

    ## function to update admin or users password base on token after resetting password
    def update_user_after_reset_password(
            self, db: Session, *,
            db_obj: ModelType,
            data: Union[UserUpdate, Dict[str, Any]]
    ):
        obj_data = jsonable_encoder(db_obj)
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db_obj.password = pwd_context.hash(data.password)
        db_obj.reset_password_token = None

        db.add(db_obj)
        db.flush()
        db.commit()
        db.refresh(db_obj)
        return db_obj


user_actions = CRUDUser(User)
