from fastapi import APIRouter

from .test import router as test_router
from .html import router as html_router


router = APIRouter()

router.include_router(test_router)
router.include_router(html_router)