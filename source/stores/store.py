from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from scripts.firewall_validator import firewall_validate_factory as FVF
from scripts.base_context import build_base_context

from LyPayAPI.store.info import get as get_store
from LyPayAPI.store.items import get_all as get_item_ids, get as get_item
from LyPayAPI.store.settings.avatar import get as get_avatar

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/stores/{ID}", response_class=HTMLResponse)
async def store_page(
        ID: str,
        request: Request,
        firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)

    store = await get_store(ID)

    avatar_url = "/static/skill_issue.jpg"
    if store.get("avatar"):
        try:
            api_answer = await get_avatar(ID)
            if api_answer is not None:
                avatar_path, _ = api_answer
                avatar_url = '/' + avatar_path
        except Exception:
            pass

    item_ids = await get_item_ids(ID, active_filter=True)
    items = []
    for item_id in item_ids:
        item = await get_item(item_id)
        items.append(item)

    return templates.TemplateResponse(
        "stores/store.html",
        await build_base_context(
            request,
            active_tab="stores",
            extra={
                "store": store,
                "avatar": avatar_url,
                "items": items,
            },
        ),
    )
