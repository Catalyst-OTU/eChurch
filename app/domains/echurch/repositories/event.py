from crud.base import CRUDBase
from domains.echurch.models.event import ChurchEvent
from domains.echurch.schemas.event import ChurchEventCreate, ChurchEventUpdate


class CRUDChurchEvent(CRUDBase[ChurchEvent, ChurchEventCreate, ChurchEventUpdate]):
    pass


church_event_repo = CRUDChurchEvent(ChurchEvent)

