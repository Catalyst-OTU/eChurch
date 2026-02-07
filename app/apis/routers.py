from fastapi import APIRouter
from domains.auth.apis import auth_routers
from domains.etransport.apis import etransport_router

router = APIRouter()
router.include_router(auth_routers)
# router.include_router(etransport_router)