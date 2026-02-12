from fastapi import APIRouter

from .departments import departments_router
from .locations import locations_router
from .centres import centres_router
from .members import members_router
from .groups import groups_router, pacentas_router
from .attendance import attendance_router
from .events import events_router
from .finance import finance_router
from .messaging import messaging_router
from .reports import reports_router
from .dashboard import dashboard_router
from .admin_tools import admin_tools_router


echurch_router = APIRouter(prefix="/echurch")
echurch_router.include_router(dashboard_router, tags=["DASHBOARD"])
echurch_router.include_router(members_router, tags=["MEMBERS"])
echurch_router.include_router(attendance_router, tags=["ATTENDANCE"])
echurch_router.include_router(events_router, tags=["EVENTS"])
echurch_router.include_router(groups_router, tags=["GROUPS"])
echurch_router.include_router(pacentas_router, tags=["PACENTAS"])
echurch_router.include_router(departments_router, tags=["DEPARTMENTS"])
echurch_router.include_router(locations_router, tags=["LOCATIONS"])
echurch_router.include_router(centres_router, tags=["CENTRES"])
echurch_router.include_router(finance_router, tags=["FINANCE"])
echurch_router.include_router(messaging_router, tags=["MESSAGING"])
echurch_router.include_router(reports_router, tags=["REPORTS"])
echurch_router.include_router(admin_tools_router, tags=["ADMIN TOOLS"])
