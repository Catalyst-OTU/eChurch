from typing import List

from domains.auth.models.users import User
from sqlalchemy.orm import Session

from domains.echurch.models.messaging import OutboundMessage, OutboundMessageRecipient
from domains.echurch.models.member import Member, Visitor
from domains.echurch.schemas.member import RecipientSchema
from domains.echurch.schemas.messaging import SendMessageRequest, SendMessageResponse


class MessagingService:
    def list_recipients(self, db: Session, *, search: str | None = None) -> List[RecipientSchema]:
        members_q = db.query(Member).filter(Member.is_deleted.is_(False)).filter(Member.is_active.is_(True))
        visitors_q = db.query(Visitor).filter(Visitor.is_deleted.is_(False)).filter(Visitor.is_active.is_(True))
        if search:
            pattern = f"%{search.strip()}%"
            members_q = members_q.filter(Member.full_name.ilike(pattern))
            visitors_q = visitors_q.filter(Visitor.full_name.ilike(pattern))
        members = members_q.order_by(Member.full_name.asc()).all()
        visitors = visitors_q.order_by(Visitor.full_name.asc()).all()

        results: List[RecipientSchema] = []
        for m in members:
            results.append(
                RecipientSchema(
                    id=m.id,
                    recipient_type="member",
                    full_name=m.full_name,
                    phone_number=m.phone_number,
                    email=m.email,
                )
            )
        for v in visitors:
            results.append(
                RecipientSchema(
                    id=v.id,
                    recipient_type="visitor",
                    full_name=v.full_name,
                    phone_number=v.phone_number,
                    email=v.email,
                )
            )
        return results

    def send_message(self, db: Session, *, data: SendMessageRequest, current_user: User) -> SendMessageResponse:
        msg = OutboundMessage(
            channel=data.channel,
            message=data.message,
            status="queued",
            created_by_user_id=current_user.id,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)

        recipients: List[OutboundMessageRecipient] = []
        for ref in data.recipients:
            if ref.recipient_type == "member":
                recipients.append(OutboundMessageRecipient(outbound_message_id=msg.id, member_id=ref.id))
            else:
                recipients.append(OutboundMessageRecipient(outbound_message_id=msg.id, visitor_id=ref.id))

        if recipients:
            db.add_all(recipients)
            db.commit()

        return SendMessageResponse(message_id=msg.id, recipients_count=len(recipients))


messaging_service = MessagingService()

