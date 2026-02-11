from crud.base import CRUDBase
from domains.echurch.models.centre import Centre
from domains.echurch.schemas.centre import CentreCreate, CentreUpdate


class CRUDCentre(CRUDBase[Centre, CentreCreate, CentreUpdate]):
    pass


centre_repo = CRUDCentre(Centre)

