from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from aiofiles import open as a_open


router = APIRouter()


@router.get("/qq")
async def QQ_skill_issue():
    async with a_open("html/test.html", encoding="utf-8") as content:
        return HTMLResponse(content=await content.read())
