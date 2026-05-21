from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.user.info import qr

from scripts.base_context import build_base_context
from scripts.firewall_validator import firewall_validate_factory as FVF


router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/card/deposit", response_class=HTMLResponse)
async def deposit_page(
        request: Request,
        firewall_ok=D(FVF("main")),
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse("/login", status_code=303)
    print(user_info)
    qr_path = "/static/skill_issue.jpg" # todo: нужна картинка типа ошибка загрузки
    try:
        qr_path = await qr(user_info["ID"])
        qr_path = "/" + qr_path
    except Exception as e:
        pass
    return templates.TemplateResponse(
        "card/deposit.html",
        await build_base_context(request, active_tab="card", extra={"qr": qr_path}),
    )
