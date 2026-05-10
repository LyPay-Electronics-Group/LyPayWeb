from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from scripts.firewall_validator import firewall_validate_factory as FVF

from LyPayAPI.store.info import get, get_by_shopkeeper, get_all_shopkeepers
from LyPayAPI.store.access import remove as access_remove

router = APIRouter()
templates = Jinja2Templates(directory="html/store/access")


@router.get("/", response_class=HTMLResponse)
async def access_page(
        request: Request,
        firewall_ok = D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse("/login", status_code=303)

    current_storeID = await get_by_shopkeeper(user_info["ID"])
    if (await get(current_storeID))["hostID"] != user_info["ID"]:
        return RedirectResponse("/store", status_code=303)

    return templates.TemplateResponse(
        "access.html",
        {
            "request": request,
            "store": await get(current_storeID),
            "shopkeepers": [
                sk for sk in await get_all_shopkeepers()
                if await get_by_shopkeeper(sk) == current_storeID and sk != user_info["ID"]
            ],
        }
    )


@router.get("/remove")
async def remove(
        ID: int,
        request: Request,
        firewall_ok = D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse("/login", status_code=303)

    current_storeID = await get_by_shopkeeper(user_info["ID"])
    if (await get(current_storeID))["hostID"] != user_info["ID"]:
        return RedirectResponse("/store", status_code=303)

    if ID == user_info["ID"]:
        return JSONResponse({"error": True}, status_code=403)

    await access_remove(current_storeID, ID)
    return JSONResponse({"ok": True}, status_code=200)
