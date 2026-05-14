from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.store.info import get, get_by_shopkeeper

from scripts.firewall_validator import firewall_validate_factory as FVF

from scripts.base_context import build_base_context

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        firewall_ok = D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "store/index.html",
        await build_base_context(
            request,
            active_tab="stores",
            extra={"store": await get(await get_by_shopkeeper(user_info["ID"]))},
        ),
    )
