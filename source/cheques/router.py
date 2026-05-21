from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.store.cheques import get as get_cheque
from LyPayAPI.store.info import get as get_store
from LyPayAPI.store.items import get as get_item
from LyPayAPI.store.settings.avatar import get as get_avatar

from scripts.base_context import build_base_context
from scripts.firewall_validator import firewall_validate_factory as FVF

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/stores/cheques/{chequeID}", response_class=HTMLResponse)
async def confirm_page(
        chequeID: str,
        request: Request,
        firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse(url="/login", status_code=303)
    try:
        cheque = await get_cheque(chequeID)
    except Exception as e:
        return RedirectResponse(url="/cheques", status_code=303)  # todo: fix
    store = await get_store(cheque["storeID"])

    avatar_url = "/static/skill_issue.jpg"
    if store.get("avatar"):
        try:
            api_answer = await get_avatar(store["ID"])
            if api_answer is not None:
                avatar_path, _ = api_answer
                avatar_url = '/' + avatar_path
        except Exception:
            pass

    lines = []
    total = 0
    for item_id, qty in cheque["items"].items():
        item = await get_item(item_id)
        price = int(item.get("price") or 0)
        line_total = price * int(qty)
        total += line_total
        lines.append(
            {
                "name": item.get("name"),
                "price": price,
                "qty": int(qty),
                "line_total": line_total,
            }
        )

    return templates.TemplateResponse(
        "cheques/cheques.html",
        await build_base_context(
            request,
            extra={
                "store": store,
                "avatar": avatar_url,
                "cheque": cheque,
                "lines": lines,
                "total": total,
            },
        ),
    )
