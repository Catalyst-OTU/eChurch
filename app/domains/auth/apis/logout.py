from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from utils.rbac import get_current_user_db

from db.session import get_db
from domains.auth.services.logout import logout_user

logout_auth_router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@logout_auth_router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_current_user_db)):
    return logout_user(request=request, response=response, db=db)
