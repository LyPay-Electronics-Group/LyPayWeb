import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates


from LyPayAPI.admin.info import core_machine, local_machine
from LyPayAPI.__exceptions__ import APIError

router = APIRouter()
templates = Jinja2Templates(directory="html/mst")

@router.get("/machine")
async def machine_page(request: Request):
    return templates.TemplateResponse("machine.html", {"request": request})

@router.get("/machine/local_stats")
async def machine_stats():
    try:
        data = await asyncio.to_thread(local_machine)
        return JSONResponse(content=data)
    except APIError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/machine/core_stats")
async def core_stats():
    try:
        data = await core_machine()
        return JSONResponse(content=data)
    except APIError as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)