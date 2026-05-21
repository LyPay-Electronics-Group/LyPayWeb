from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from scripts.firewall_validator import firewall_validate_factory as FVF
from scripts.base_context import build_base_context

from LyPayAPI.store.info import get as get_store, get_all_ids
from LyPayAPI.store.settings.avatar import get as get_avatar

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/stores", response_class=HTMLResponse)
async def stores_index(
    request: Request,
    firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login", status_code=303)

    store_ids = await get_all_ids()
    stores = []

    for store_id in store_ids:
        store = await get_store(store_id)
        avatar_url = "/static/skill_issue.jpg"

        if store.get("avatar"):
            try:
                api_answer = await get_avatar(store_id)
                if api_answer is not None:
                    avatar_path, _ = api_answer
                    avatar_url = '/' + avatar_path
            except Exception:
                pass

        stores.append(
            {
                "ID": store.get("ID"),
                "name": store.get("name"),
                "description": store.get("description") or "",
                "avatar": avatar_url,
            }
        )

    return templates.TemplateResponse(
        "stores/index.html",
        await build_base_context(
            request,
            active_tab="stores",
            extra={"stores": stores},
        ),
    )

