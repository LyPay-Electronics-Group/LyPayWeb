from fastapi import APIRouter

from .index import router as index_router
from .deposit import router as deposit_router
from .transfer import router as transfer_router


router = APIRouter()
router.include_router(index_router)
router.include_router(deposit_router)
router.include_router(transfer_router)
