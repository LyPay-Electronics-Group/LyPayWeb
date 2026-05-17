from fastapi import APIRouter

from .register import router as register_router
from .access import router as access_router
from .items import router as items_settings_router
from .index import router as base_router
from .settings import router as settings_router


router = APIRouter()
router.include_router(base_router)
router.include_router(register_router, prefix="/register")
router.include_router(access_router, prefix="/access")
router.include_router(items_settings_router, prefix="/items")
router.include_router(settings_router, prefix="/settings")
