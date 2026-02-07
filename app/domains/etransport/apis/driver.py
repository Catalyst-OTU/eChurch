from typing import Any, List, Literal
from utils.cls import ContentQueryChecker
from fastapi import APIRouter, Depends, status, Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.orm import Session
from config.settings import settings
from db.session import get_db
from domains.auth.apis.login import send_reset_email
from domains.etransport.models import Driver
from domains.etransport.schemas import driver as schemas
from domains.auth.schemas.password_reset import ResetPasswordRequest
from domains.auth.services.password_reset import password_reset_service
from domains.etransport.services.driver import drivers_service as actions
from services.email_service import Email
from utils.rbac import check_if_is_system_admin, get_current_user
from utils.schemas import HTTPError


drivers_router = APIRouter(
    prefix="/Drivers",
    responses={404: {"description": "Not found"}},
)


# @drivers_router.post("/Drivers/")
# def create_Driver(Driver: schemas.DriverCreate, request: Request, db: Session = Depends(get_db)):
#     schema = request.state.schema

#     if not schema:
#         raise HTTPException(status_code=400, detail="Schema not found")

#     Driver.__table__.schema = schema  

#     new_Driver = Driver(**Driver.dict())
#     db.add(new_Driver)
#     db.commit()

#     return {"message": "Driver created successfully in schema " + schema}


@drivers_router.get(
    "/",
    response_model=List[schemas.DriverSchema]
)
def list_Drivers(
                    *, 
                    db: Session = Depends(get_db),
                    current_Driver: Driver = Depends(check_if_is_system_admin),
                    skip: int = 0,
                    limit: int = 100,
                    order_by: str = None,
                    order_direction: Literal['asc', 'desc'] = 'asc'
                     ) -> Any:
    Drivers = actions.list_Drivers(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return Drivers




# @drivers_router.get(
#     "/",
#     response_model=schemas.DriverResponse
# )
# @ContentQueryChecker(Driver.c(), None)
# def list_Drivers(
#                     *, 
#                     db: Session = Depends(get_db),
#                     current_Driver: Driver = Depends(check_if_is_system_admin),
                    
#                     request: Request,
#                      ) -> Any:
#     Drivers = Driver_repo.special_read(request, db)
#     return Drivers


@drivers_router.post(
    "/",
    response_model=schemas.DriverSchema,
    status_code=status.HTTP_201_CREATED
)
def create_Driver(
        *,
        #organization_id: UUID4,
        #current_Driver: Driver = Depends(get_current_user),
        Driver_in: schemas.DriverCreate,
        db: Session = Depends(get_db)
) -> Any:
    Driver = actions.create_Driver(Driver_in=Driver_in, db=db)
    return Driver


@drivers_router.put(
    "/{id}",
    response_model=schemas.DriverSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_Driver(
        *, db: Session = Depends(get_db),
        current_Driver: Driver = Depends(get_current_user),
        id: UUID4,
        Driver_in: schemas.DriverUpdate,
) -> Any:
    Driver = actions.update_Driver(db=db, id=id, Driver_in=Driver_in)
    return Driver


@drivers_router.get(
    "/{id}",
    response_model=schemas.DriverSchema
)
def get_Driver(
        *, db: Session = Depends(get_db),
        current_Driver: Driver = Depends(get_current_user),
        id: UUID4
) -> Any:
    Driver = actions.get_Driver(db=db, id=id)
    return Driver


@drivers_router.delete(
    "/{id}",
    response_model=schemas.UserSchema
)
def block_Driver(
        *, db: Session = Depends(get_db),
        current_Driver: Driver = Depends(check_if_is_system_admin),
        id: UUID4,
        soft_delete: bool
) -> Any:
    Driver = actions.block_Driver(db=db, id=id, soft_delete=soft_delete)
    return Driver





@drivers_router.post(
    "/activate-account/{id}",
    #response_model=schemas.UserSchema
)
def activate_Driver_account(
        *, db: Session = Depends(get_db),
        current_Driver: Driver = Depends(check_if_is_system_admin),
        id: UUID4
) -> Any:
    Driver = actions.activate_Driver_account(db=db, id=id)
    return "Account activated succesfully"



@drivers_router.get(
    "/user-profile/{email}",
    response_model=schemas.UserSchema
)
def get_Driver_profile_by_email(
        *, db: Session = Depends(get_db),
        current_Driver: Driver = Depends(get_current_user),
        email: str
) -> Any:
    Driver = actions.get_Driver_profile_by_email(db=db, email=email)
    return Driver








@drivers_router.delete(
    "/delete-account/{id}",
    #response_model=schemas.UserSchema
)
def delete_account_for_Driver(
        *, db: Session = Depends(get_db),
        current_Driver: Driver = Depends(get_current_user),
        id: UUID4
) -> Any:
    Driver = actions.delete_account_for_Driver(db=db, id=id)
    return "Account deleted successfully"