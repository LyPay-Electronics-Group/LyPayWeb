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
    if request.session.get("mst") is not None:
        session_data = dict(request.session["mst"])
    else:
        session_data = dict()
    return templates.TemplateResponse("results.html", {
        "request": request,
        "session_data": session_data
    })


@router.post("/results/clear")
async def clear_session(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)
    request.session["mst"] = dict()
    return {"status": "ok", "message": "Сессия очищена"}
