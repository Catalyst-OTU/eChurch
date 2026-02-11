from typing import List, Literal, Optional

from pydantic import BaseModel, UUID4

from db.schemas import BaseSchema


Channel = Literal["WhatsApp", "Email"]


class RecipientRef(BaseModel):
    recipient_type: Literal["member", "visitor"]
    id: UUID4


class SendMessageRequest(BaseModel):
    channel: Channel
    message: str
    recipients: List[RecipientRef]


class OutboundMessageSchema(BaseSchema):
    channel: Channel
    message: str
    status: str
    created_by_user_id: Optional[UUID4] = None


class SendMessageResponse(BaseModel):
    message_id: UUID4
    recipients_count: int

