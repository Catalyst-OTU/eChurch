from typing import Any, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.users import User
from domains.echurch.schemas.member import RecipientsResponse
from domains.echurch.schemas.messaging import SendMessageRequest, SendMessageResponse
from domains.echurch.services.messaging import messaging_service
from utils.rbac import get_current_user


messaging_router = APIRouter(prefix="/messaging", responses={404: {"description": "Not found"}})


@messaging_router.get("/recipients", response_model=RecipientsResponse)
def list_recipients(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = None,
) -> Any:
    recipients = messaging_service.list_recipients(db, search=search)
    return {"data": recipients}


@messaging_router.post("/send", response_model=SendMessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    data: SendMessageRequest,
) -> Any:
    return messaging_service.send_message(db, data=data, current_user=current_user)

