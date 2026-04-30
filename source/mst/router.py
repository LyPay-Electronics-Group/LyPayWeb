from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/")
async def mst_main_page(request: Request):
    if request.session.get("user") is None:
        pass  # TODO: проверка регистрации

    return templates.TemplateResponse("mst/index.html", {"request": request})
