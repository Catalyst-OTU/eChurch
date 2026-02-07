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
from domains.etransport.models import Passenger
from domains.etransport.schemas import passenger as schemas
from domains.auth.schemas.password_reset import ResetPasswordRequest
from domains.auth.services.password_reset import password_reset_service
from domains.etransport.services.passenger import passengers_service as actions
from services.email_service import Email
from utils.rbac import check_if_is_system_admin, get_current_user
from utils.schemas import HTTPError


passengers_router = APIRouter(
    prefix="/passengers",
    responses={404: {"description": "Not found"}},
)


# @passengers_router.post("/Passengers/")
# def create_Passenger(Passenger: schemas.PassengerCreate, request: Request, db: Session = Depends(get_db)):
#     schema = request.state.schema

#     if not schema:
#         raise HTTPException(status_code=400, detail="Schema not found")

#     Passenger.__table__.schema = schema  

#     new_Passenger = Passenger(**Passenger.dict())
#     db.add(new_Passenger)
#     db.commit()

#     return {"message": "Passenger created successfully in schema " + schema}


@passengers_router.get(
    "/",
    response_model=List[schemas.PassengerSchema]
)
def list_Passengers(
                    *, 
                    db: Session = Depends(get_db),
                    current_Passenger: Passenger = Depends(check_if_is_system_admin),
                    skip: int = 0,
                    limit: int = 100,
                    order_by: str = None,
                    order_direction: Literal['asc', 'desc'] = 'asc'
                     ) -> Any:
    Passengers = actions.list_Passengers(
        db=db, skip=skip, limit=limit, order_by=order_by, order_direction=order_direction
    )
    return Passengers




# @passengers_router.get(
#     "/",
#     response_model=schemas.PassengerResponse
# )
# @ContentQueryChecker(Passenger.c(), None)
# def list_Passengers(
#                     *, 
#                     db: Session = Depends(get_db),
#                     current_Passenger: Passenger = Depends(check_if_is_system_admin),
                    
#                     request: Request,
#                      ) -> Any:
#     Passengers = Passenger_repo.special_read(request, db)
#     return Passengers


@passengers_router.post(
    "/",
    response_model=schemas.PassengerSchema,
    status_code=status.HTTP_201_CREATED
)
def create_Passenger(
        *,
        #organization_id: UUID4,
        #current_Passenger: Passenger = Depends(get_current_user),
        Passenger_in: schemas.PassengerCreate,
        db: Session = Depends(get_db)
) -> Any:
    Passenger = actions.create_Passenger(Passenger_in=Passenger_in, db=db)
    return Passenger


@passengers_router.put(
    "/{id}",
    response_model=schemas.PassengerSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_Passenger(
        *, db: Session = Depends(get_db),
        current_Passenger: Passenger = Depends(get_current_user),
        id: UUID4,
        Passenger_in: schemas.PassengerUpdate,
) -> Any:
    Passenger = actions.update_Passenger(db=db, id=id, Passenger_in=Passenger_in)
    return Passenger


@passengers_router.get(
    "/{id}",
    response_model=schemas.PassengerSchema
)
def get_Passenger(
        *, db: Session = Depends(get_db),
        current_Passenger: Passenger = Depends(get_current_user),
        id: UUID4
) -> Any:
    Passenger = actions.get_Passenger(db=db, id=id)
    return Passenger


@passengers_router.delete(
    "/{id}",
    response_model=schemas.UserSchema
)
def block_Passenger(
        *, db: Session = Depends(get_db),
        current_Passenger: Passenger = Depends(check_if_is_system_admin),
        id: UUID4,
        soft_delete: bool
) -> Any:
    Passenger = actions.block_Passenger(db=db, id=id, soft_delete=soft_delete)
    return Passenger





@passengers_router.post(
    "/activate-account/{id}",
    #response_model=schemas.UserSchema
)
def activate_passenger_account(
        *, db: Session = Depends(get_db),
        current_Passenger: Passenger = Depends(check_if_is_system_admin),
        id: UUID4
) -> Any:
    Passenger = actions.activate_passenger_account(db=db, id=id)
    return "Account activated succesfully"



@passengers_router.get(
    "/user-profile/{email}",
    response_model=schemas.UserSchema
)
def get_Passenger_profile_by_email(
        *, db: Session = Depends(get_db),
        current_Passenger: Passenger = Depends(get_current_user),
        email: str
) -> Any:
    Passenger = actions.get_Passenger_profile_by_email(db=db, email=email)
    return Passenger








@passengers_router.delete(
    "/delete-account/{id}",
    #response_model=schemas.UserSchema
)
def delete_account_for_passenger(
        *, db: Session = Depends(get_db),
        current_Passenger: Passenger = Depends(get_current_user),
        id: UUID4
) -> Any:
    Passenger = actions.delete_account_for_passenger(db=db, id=id)
    return "Account deleted successfully"