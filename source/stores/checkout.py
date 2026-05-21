from fastapi import APIRouter, Request, Depends as D, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.store.cheques import create as create_cheque
from LyPayAPI.store.info import get as get_store
from LyPayAPI.store.items import get as get_item
from LyPayAPI.store.settings.avatar import get as get_avatar
from LyPayAPI.user.info import get as get_user_info

from scripts.base_context import build_base_context
from scripts.firewall_validator import firewall_validate_factory as FVF

router = APIRouter()
templates = Jinja2Templates(directory="html")


async def _require_user(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return user


@router.post("/stores/{ID}/cart")
async def set_cart(
        ID: str,
        request: Request,
        firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return JSONResponse({"ok": False, "error": "firewall"}, status_code=403)

    await _require_user(request)
    payload = await request.json()
    items = payload.get("items", {})

    cleaned: dict[str, int] = {}
    if isinstance(items, dict):
        for k, v in items.items():
            try:
                qty = int(v)
            except Exception:
                continue
            if qty <= 0:
                continue
            cleaned[str(k)] = min(qty, 999)

    request.session[f"stores_cart:{ID}"] = cleaned
    return JSONResponse({"ok": True})


@router.get("/stores/{ID}/checkout", response_class=HTMLResponse)
async def checkout_page(
        ID: str,
        request: Request,
        firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user = await _require_user(request)
    cart = request.session.get(f"stores_cart:{ID}", {})
    if not cart:
        return RedirectResponse(f"/stores/{ID}", status_code=303)

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

    lines = []
    total = 0
    for item_id, qty in cart.items():
        item = await get_item(item_id)
        price = int(item.get("price") or 0)
        line_total = price * int(qty)
        total += line_total
        lines.append(
            {
                "itemID": item_id,
                "name": item.get("name"),
                "price": price,
                "qty": int(qty),
                "line_total": line_total,
            }
        )

    user_info = await get_user_info(user["ID"])
    balance = int(user_info.get("balance") or 0)

    error = request.query_params.get("error")
    insufficient = balance < total

    balance_after = f"{balance - total} Тгр."

    return templates.TemplateResponse(
        "stores/checkout.html",
        await build_base_context(
            request,
            active_tab="stores",
            extra={
                "store": store,
                "avatar": avatar_url,
                "lines": lines,
                "total": total,
                "balance_after": balance_after,
                "insufficient": insufficient,
                "error": error,
            },
        ),
    )


@router.post("/stores/{ID}/pay")
async def pay(
        ID: str,
        request: Request,
        firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user = await _require_user(request)
    cart: dict[str, int] = request.session.get(f"stores_cart:{ID}", {})
    if not cart:
        return RedirectResponse(f"/stores/{ID}", status_code=303)

    try:
        cheque_id = await create_cheque(ID, user["ID"], cart)
    except Exception:
        return RedirectResponse(f"/stores/{ID}/checkout?error=Не+удалось+оплатить", status_code=303)

    request.session.pop(f"stores_cart:{ID}", None)
    return RedirectResponse(f"/stores/cheques/{cheque_id}", status_code=303)
