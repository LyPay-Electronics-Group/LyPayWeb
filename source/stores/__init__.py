from fastapi import APIRouter

from .list import router as list_router
from .store import router as store_router


router = APIRouter()
router.include_router(list_router)
router.include_router(store_router)