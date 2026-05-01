from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from asyncio import sleep
from random import randint

from scripts.unix import unix

from .utils import test3, test3_end, GLOBAL_TEST3_PARAMETER

router = APIRouter()
templates = Jinja2Templates(directory="html/mst")


@router.get("/test3")
async def test3_page(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("test3.html", {"request": request})


@router.post("/test3/run")
async def do_test3(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)
    ID = request.session.get("user")["ID"]

    start_time = unix()
    delta_time = 0
    for _ in range(GLOBAL_TEST3_PARAMETER):
        await test3(ID)

        delta_time_start = unix()
        await sleep(randint(10, 20) / 1000)
        delta_time_end = unix()

        delta_time += delta_time_end - delta_time_start
    end_time = unix()

    if request.session.get("mst") is None:
        request.session["mst"] = dict()

    if request.session.get("mst").get("test3") is None:
        request.session["mst"]["test3"] = {
            "total": GLOBAL_TEST3_PARAMETER,
            "time": end_time - start_time - delta_time,
        }
    else:
        request.session["mst"]["test3"]["total"] += GLOBAL_TEST3_PARAMETER
        request.session["mst"]["test3"]["time"] += end_time - start_time - delta_time
    return {"status": "ok"}


@router.post("/test3/end")
async def end_test3(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)

    result_local, result_core = await test3_end(request.session.get("user")["ID"])

    if request.session.get("mst") is not None and request.session.get("mst").get("test3") is not None:
        request.session["mst"]["test3"]["local"] = result_local
        request.session["mst"]["test3"]["core"] = result_core
    return {"status": "ok"}
