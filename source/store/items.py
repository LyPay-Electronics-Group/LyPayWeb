from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from scripts.firewall_validator import firewall_validate_factory as FVF

from LyPayAPI.store.info import get, get_by_shopkeeper
from LyPayAPI.store import items
from LyPayAPI.__exceptions__ import IDNotFound, UserIsAlreadyShopkeeper

from scripts.base_context import build_base_context

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/", response_class=HTMLResponse)
async def items_page(
        request: Request,
        firewall_ok = D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse("/login", status_code=303)

    current_storeID = await get_by_shopkeeper(user_info["ID"])

    return templates.TemplateResponse(
        "store/items.html",
        await build_base_context(
            request,
            active_tab="stores",
            extra={
                "store": await get(current_storeID),
                "items": [await items.get(item) for item in await items.get_all(current_storeID, active_filter=True)],
            },
        ),
    )


@router.get("/single")
async def save_edit(
        request: Request,
        ID: str = None,
        name: str = None,
        price: int = None,
        firewall_ok = D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    if ID is None or name is None or price is None:
        return JSONResponse({"error": True}, status_code=403)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse("/login", status_code=303)

    current_storeID = await get_by_shopkeeper(user_info["ID"])
    if (await items.get(ID))["storeID"] != current_storeID:
        return JSONResponse({"error": True}, status_code=403)

    try:
        await items.edit(ID, name, price)
        return JSONResponse({"ok": True}, status_code=200)
    except IDNotFound, UserIsAlreadyShopkeeper:
        return JSONResponse({"error": True}, status_code=403)


@router.get("/add")
async def add(
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

    try:
        await items.add(current_storeID, "test", 0)
        return JSONResponse({"ok": True}, status_code=200)
    except IDNotFound, UserIsAlreadyShopkeeper:
        return JSONResponse({"error": True}, status_code=403)
