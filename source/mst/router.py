from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="html/mst")


@router.get("/")
async def mst_main_page(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/results")
async def session_results(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)
    if request.session.get("mst") is not None and request.session.get("mst").get("test1") is not None:
        test1 = dict(request.session["mst"]["test1"])
    else:
        test1 = dict()
    if request.session.get("mst") is not None and request.session.get("mst").get("test2") is not None:
        test2 = dict(request.session["mst"]["test2"])
    else:
        test2 = dict()
    if request.session.get("mst") is not None and request.session.get("mst").get("test3") is not None:
        test3 = dict(request.session["mst"]["test3"])
    else:
        test3 = dict()
    return templates.TemplateResponse("results.html", {
        "request": request,
        "test1": test1,
        "test2": test2,
        "test3": test3,
    })


@router.post("/results/clear")
async def clear_session(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)
    request.session["mst"] = dict()
    return {"status": "ok", "message": "Сессия очищена"}
