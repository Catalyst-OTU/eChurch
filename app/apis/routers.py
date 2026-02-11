from fastapi import APIRouter
from domains.auth.apis import auth_routers
from domains.echurch.apis import echurch_router

router = APIRouter()
router.include_router(auth_routers)
router.include_router(echurch_router)
