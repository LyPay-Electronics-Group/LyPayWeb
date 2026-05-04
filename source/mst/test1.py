from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from scripts.unix import unix

from .utils import test1

router = APIRouter()
templates = Jinja2Templates(directory="html/mst")


@router.get("/test1")
async def test1_page(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("test1.html", {"request": request})


@router.post("/test1/run")
async def do_test1(request: Request):
    start_time = unix()
    test_result = await test1()
    end_time = unix()

    if request.session.get("mst") is None:
        request.session["mst"] = dict()

    if request.session.get("mst").get("test1") is None:
        request.session["mst"]["test1"] = {
            "total": 1,
            "success": int(test_result),
            "time": end_time - start_time,
        }
    else:
        request.session["mst"]["test1"]["total"] += 1
        request.session["mst"]["test1"]["success"] += int(test_result)
        request.session["mst"]["test1"]["time"] += end_time - start_time
    return {"status": "ok"}
