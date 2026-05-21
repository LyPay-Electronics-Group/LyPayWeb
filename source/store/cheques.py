from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse

from scripts.firewall_validator import firewall_validate_factory as FVF
from datetime import datetime

from LyPayAPI.store.info import get, get_by_shopkeeper
from LyPayAPI.store import items, cheques

from scripts.base_context import build_base_context

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/", response_class=HTMLResponse)
async def cheques_page(
        request: Request,
        firewall_ok = D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse("/login", status_code=303)

    current_storeID = await get_by_shopkeeper(user_info["ID"])

    cheques_base = list()
    for cheque in await cheques.get_all(current_storeID, False):
        cheque = await cheques.get(cheque)
        items_parsed = list()
        total = 0
        for item, multi in cheque["items"].items():
            item = await items.get(item)
            items_parsed.append({
                "name": item["name"],
                "price": item["price"],
                "multiplier": multi
            })
            total += multi * item["price"]
        cheques_base.append((
            {
                "chequeID": cheque["chequeID"],
                "items_parsed": items_parsed,
                "total": total,
                "timestamp": datetime.fromtimestamp(cheque["unix"]).strftime("%H:%M:%S"),
                "active": cheque["active"]
            },
            cheque["unix"]
        ))


    return templates.TemplateResponse(
        "store/cheques.html",
        await build_base_context(
            request,
            extra={
                "store": await get(current_storeID),
                "cheques": map(lambda c: c[0], sorted(cheques_base, key=lambda c: c[1], reverse=True)),
            },
        ),
    )


@router.get("/cancel")
async def cancel_cheque(
        request: Request,
        ID: str = None,
        firewall_ok = D(FVF('stores'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse("/login", status_code=303)

    if ID is None:
        return JSONResponse({"error": True}, status_code=404)

    current_storeID = await get_by_shopkeeper(user_info["ID"])
    if (await cheques.get(ID))["storeID"] != current_storeID:
        return JSONResponse({"error": True}, status_code=403)

    try:
        await cheques.cancel(ID)
        return JSONResponse({"ok": True}, status_code=200)
    except Exception:
        return JSONResponse({"error": True}, status_code=400)
