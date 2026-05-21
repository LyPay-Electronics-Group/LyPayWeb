from fastapi import APIRouter

from .list import router as list_router
from .store import router as store_router
from .checkout import router as checkout_router


router = APIRouter()
router.include_router(list_router)
router.include_router(store_router)
router.include_router(checkout_router)