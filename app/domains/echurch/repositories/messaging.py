from crud.base import CRUDBase
from domains.echurch.models.messaging import OutboundMessage, OutboundMessageRecipient
from domains.echurch.schemas.messaging import SendMessageRequest


class CRUDOutboundMessage(CRUDBase[OutboundMessage, SendMessageRequest, SendMessageRequest]):
    pass


class CRUDOutboundMessageRecipient(CRUDBase[OutboundMessageRecipient, dict, dict]):
    pass


outbound_message_repo = CRUDOutboundMessage(OutboundMessage)
outbound_message_recipient_repo = CRUDOutboundMessageRecipient(OutboundMessageRecipient)

