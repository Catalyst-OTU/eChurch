from typing import Any, List, Literal
from utils.cls import ContentQueryChecker
from fastapi import APIRouter, Depends, status, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from domains.auth.respository.user_account import User
from config.settings import settings
from db.session import get_db
from domains.auth.apis.login import send_reset_email
from domains.auth.models.users import User
from domains.auth.schemas import user_account as schemas
from domains.auth.schemas.password_reset import ResetPasswordRequest
from domains.auth.services.password_reset import password_reset_service
from domains.auth.services.user_account import users_forms_service as actions
from domains.auth.services.user_account import user_repo
from services.email_service import Email
from utils.rbac import check_if_is_system_admin, get_current_user_db
from utils.schemas import HTTPError


users_router = APIRouter(
    responses={404: {"description": "Not found"}},
)


# @users_router.post("/users/")
# def create_user(user: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
#     schema = request.state.schema

#     if not schema:
#         raise HTTPException(status_code=400, detail="Schema not found")

#     User.__table__.schema = schema  

#     new_user = User(**user.dict())
#     db.add(new_user)
#     db.commit()

#     return {"message": "User created successfully in schema " + schema}


@users_router.get(
    "/",
    response_model=List[schemas.UserSchema]
)
def list_users(
                    *, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(check_if_is_system_admin),
                    skip: int = 0,
                    limit: int = 100,
                    order_by: str = None,
                    order_direction: Literal['asc', 'desc'] = 'asc'
                     ) -> Any:
    users = actions.list_users(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return users




# @users_router.get(
#     "/",
#     response_model=schemas.UserResponse
# )
# @ContentQueryChecker(User.c(), None)
# def list_users(
#                     *, 
#                     db: Session = Depends(get_db),
#                     current_user: User = Depends(check_if_is_system_admin),
                    
#                     request: Request,
#                      ) -> Any:
#     users = user_repo.special_read(request, db)
#     return users


@users_router.post(
    "/",
    response_model=schemas.UserSchema,
    status_code=status.HTTP_201_CREATED
)
def create_user(
        *,
        #organization_id: UUID4,
        current_user: User = Depends(check_if_is_system_admin),
        user_in: schemas.UserCreate,
        db: Session = Depends(get_db)
) -> Any:
    user = actions.create_user(user_in=user_in, db=db)
    return user


@users_router.put(
    "/{id}",
    response_model=schemas.UserSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4,
        user_in: schemas.UserUpdate,
) -> Any:
    user = actions.update_user(db=db, id=id, user_in=user_in)
    return user


@users_router.get(
    "/{id}",
    response_model=schemas.UserSchema
)
def get_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4
) -> Any:
    user = actions.get_user(db=db, id=id)
    return user


@users_router.delete(
    "/{id}",
    response_model=schemas.UserSchema
)
def delete_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(check_if_is_system_admin),
        id: UUID4
) -> None:
    actions.delete_user(db=db, id=id)


@users_router.post(
    "/forgot_password/"
)
def request_password_reset(
        *, db: Session = Depends(get_current_user_db),
        reset_password_request: ResetPasswordRequest,
):
    user = actions.repo.get_by_email(db=db, email=reset_password_request.email, silent=False)

    token = password_reset_service.generate_reset_token()
    user.reset_password_token = token
    db.commit()

    reset_link = f"{settings.FRONTEND_URL}/login/resetpassword?token={token}"
    email_data = send_reset_email(user.username, user.email, reset_link)

    Email.sendMailService(email_data, template_name='forgot-password.html')
    return JSONResponse(content={"message": "Password reset link has been sent to your email."}, status_code=200)


@users_router.put(
    "/reset_password_token/{token}",
    response_model=schemas.UserSchema
)
def update_user_with_reset_password_token(
        *, db: Session = Depends(get_current_user_db),
        token: str,
        data: schemas.UpdatePassword
):
    update_user = actions.repo.get_by_reset_password_token(db=db, token=token)
    if not update_user: raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Token"
    )
    data = actions.repo.update_user_after_reset_password(db=db, db_obj=update_user, data=data)
    return data
