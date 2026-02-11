from crud.base import CRUDBase
from domains.echurch.models.location import Location
from domains.echurch.schemas.location import LocationCreate, LocationUpdate


class CRUDLocation(CRUDBase[Location, LocationCreate, LocationUpdate]):
    pass


location_repo = CRUDLocation(Location)

