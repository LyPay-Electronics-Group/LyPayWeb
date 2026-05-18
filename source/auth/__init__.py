from fastapi import APIRouter

from .main import router as main_router
from .guest import router as guest_router
from .login import router as login_router


router = APIRouter()
router.include_router(main_router, prefix="/register")
router.include_router(guest_router, prefix="/register_guest")
router.include_router(login_router)
