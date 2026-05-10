from fastapi import APIRouter, Request, Form, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from scripts.firewall_validator import firewall_validate_factory as FVF

router = APIRouter()
templates = Jinja2Templates(directory="html/store/access")


@router.get("/", response_class=HTMLResponse)
async def access_page(
        request: Request,
        firewall_ok = D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse("access.html", {"request": request})
