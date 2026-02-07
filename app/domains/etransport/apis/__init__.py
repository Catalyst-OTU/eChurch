from fastapi import APIRouter

from .passenger import passengers_router
from .driver import drivers_router

etransport_router = APIRouter()
etransport_router.include_router(drivers_router, tags=["DRIVERS ACCOUNT"])
etransport_router.include_router(passengers_router, tags=["PASSENGERS ACCOUNT"])
