from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from scripts.firewall_validator import firewall_validate_factory as FVF

from LyPayAPI.store.info import get, get_by_shopkeeper
from LyPayAPI.store import access
from LyPayAPI.__exceptions__ import IDNotFound, UserIsAlreadyAShopkeeper

from scripts.base_context import build_base_context

router = APIRouter()
templates = Jinja2Templates(directory="html")


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
        return RedirectResponse("/store/", status_code=303)

    return templates.TemplateResponse(
        "store/access.html",
        await build_base_context(
            request,
            extra={
                "store": await get(current_storeID),
                "shopkeepers": [sk for sk in await access.get_list(current_storeID) if sk != user_info["ID"]],
            },
        ),
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
        return RedirectResponse("/store/", status_code=303)

    if ID == user_info["ID"]:
        return JSONResponse({"error": True}, status_code=403)

    try:
        await access.remove(current_storeID, ID)
        return JSONResponse({"ok": True}, status_code=200)
    except IDNotFound:
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
        return RedirectResponse("/store/", status_code=303)

    if ID == user_info["ID"]:
        return JSONResponse({"error": True}, status_code=403)

    try:
        await access.add(current_storeID, ID)
        return JSONResponse({"ok": True}, status_code=200)
    except IDNotFound, UserIsAlreadyAShopkeeper:
        return JSONResponse({"error": True}, status_code=403)
