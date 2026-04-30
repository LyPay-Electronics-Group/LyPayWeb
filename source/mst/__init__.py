from fastapi import APIRouter

from .router import router as main_router
from .test1 import router as test1_router
from .test2 import router as test2_router
from .test3 import router as test3_router
from .machine import router as machine_router


router = APIRouter()
router.include_router(main_router)
router.include_router(test1_router)
router.include_router(test2_router)
router.include_router(test3_router)
router.include_router(machine_router)
