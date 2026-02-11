from crud.base import CRUDBase
from domains.echurch.models.member import Member, Visitor
from domains.echurch.schemas.member import MemberCreate, MemberUpdate, VisitorCreate, VisitorUpdate


class CRUDMember(CRUDBase[Member, MemberCreate, MemberUpdate]):
    pass


class CRUDVisitor(CRUDBase[Visitor, VisitorCreate, VisitorUpdate]):
    pass


member_repo = CRUDMember(Member)
visitor_repo = CRUDVisitor(Visitor)

