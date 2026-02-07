from typing import Any, List, Literal
from domains.auth.models import User
from fastapi import APIRouter, Depends, status, Request, Header, HTTPException
from pydantic import UUID4
from sqlalchemy.orm import Session
from utils.rbac import get_current_user
from db.session import get_db
from domains.auth.schemas import roles as schemas
from domains.auth.services.role import role_service as actions
from utils.schemas import HTTPError
from utils.cls import ContentQueryChecker
from domains.auth.respository.role import role_crud as role_repo
from domains.auth.models.role_permissions import Role

role_router = APIRouter(
    prefix="/roles",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)



@role_router.post("/", response_model=schemas.RoleSchema)
def create_role(
                    *, db: Session = Depends(get_db),
                    #current_user: User = Depends(get_current_user),
                    data: schemas.RolePermissionsCreate, 
                    
                      ):

    roles = actions.create_role(db, data=data)
    return roles





@role_router.get("/", response_model=List[schemas.RoleResponse])
#@ContentQueryChecker(Role.c(), None)
def get_roles(
                    *, 
                    
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db),
                    skip: int = 0,
                    limit: int = 100,
                    order_by: str = None,
                    order_direction: Literal['asc', 'desc'] = 'asc'
                    
):
    """Fetch all roles under a specific organization."""

    roles = role_repo.get_all(db=db, skip=skip, limit=limit)        
    return roles








@role_router.put(
    "/{id}",
    response_model=schemas.RoleSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def update_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        data: schemas.RolePermissionsUpdate,
        
) -> Any:
    role = actions.update_role(db=db, id=id, data=data)
    return role


@role_router.get(
    "/{id}",
    response_model=schemas.RoleSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def get_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> Any:
    role = actions.get_role(db=db, id=id)
    return role


@role_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
def delete_role(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4,
        
) -> None:
    actions.delete_role(db=db, id=id)














# @role_router.post("/")
# def create_role(role_in: RoleCreate, request: Request, db: Session = Depends(get_db)):
#     schema = request.state.schema  # Ensure schema is extracted from request
#     # print("Schema in API:", schema)

#     role = actions.create_role(schema, db, role_in=role_in)
#     return role

