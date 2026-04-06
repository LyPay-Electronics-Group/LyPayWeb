from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/test")
async def test(ID: int = None):
    return JSONResponse({"ID": ID}, status_code=200)
