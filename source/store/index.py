from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.store.info import get, get_by_shopkeeper
from LyPayAPI.store.items import get_all, get as get_item
from LyPayAPI.store.settings.avatar import get as get_avatar
from scripts.base_context import build_base_context
from scripts.firewall_validator import firewall_validate_factory as FVF

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        firewall_ok=D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse("/login", status_code=303)

    try:
        store_id = await get_by_shopkeeper(user_info["ID"])
        store_info = await get(store_id)
    except Exception as e:
        return HTMLResponse(content=f"Ошибка: {str(e)}", status_code=500)

    clean_shop_info = {
        "ID": store_info["ID"],
        "Название": store_info["name"],
        "Описание": store_info["description"],
        "Владелец": store_info["hostID"],
        "Баланс": store_info["balance"],
    }

    try:
        api_answer = await get_avatar(store_id)
        if api_answer is not None:
            avatar_path, _ = api_answer
            avatar_url = '/' + avatar_path
        else:
            raise Exception
    except Exception:
        avatar_url = "/static/skill_issue.jpg"

    try:
        items_id = await get_all(store_id)
        items = {}
        for item_id in items_id:
            items[item_id] = await get_item(item_id)
    except Exception as e:
        return HTMLResponse(content=f"Ошибка: {str(e)}", status_code=500)
    print(items)
    return templates.TemplateResponse(
        "store/index.html",
        await build_base_context(
            request,
            active_tab="stores",
            extra={"store": clean_shop_info,
                   "avatar": avatar_url,
                   "items": items},
        ),
    )
