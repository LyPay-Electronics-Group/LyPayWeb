from fastapi import APIRouter, Request, Depends as D
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.user import transactions
from LyPayAPI.store.items import get as get_item

from scripts.j2 import from_ as j2_from
from scripts.base_context import build_base_context
from scripts.firewall_validator import firewall_validate_factory as FVF

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/card", response_class=HTMLResponse)
async def index(
        request: Request,
        firewall_ok=D(FVF('main'))
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse("/login", status_code=303)

    user_transfers_out = [
        (dict(zip(("type", "ID", "amount"), ("out", tr[0][1:], tr[1]))), tr[2])
        for tr in await transactions.transfer_history(ID_out=user_info["ID"])
    ]
    user_transfers_in = [
        (dict(zip(("type", "ID", "amount"), ("in", tr[0][1:], tr[1]))), tr[2])
        for tr in await transactions.transfer_history(ID_in=user_info["ID"])
    ]
    user_deposits = [
        (dict(zip(("type", "amount"), ("deposit", tr[0]))), tr[1])
        for tr in await transactions.deposit_history(user_info["ID"])
    ]
    user_cheques = list()
    for cheque in await transactions.cheque_history(user_info["ID"]):
        items_parsed = j2_from(cheque[1])
        displaying_items = list()
        total_sum = 0
        for itemID, multiplier in items_parsed.items():
            item_data = await get_item(itemID)
            total_sum += item_data['price'] * multiplier
            displaying_items.append((item_data['name'], multiplier))
        user_cheques.append((
            dict(zip(
                ("type",   "storeID",  "display_items",   "amount"),
                ("cheque",  cheque[0],  displaying_items,  total_sum)
            )),
            cheque[2]
        ))

    transaction_history = list()
    transaction_history.extend(user_transfers_in)
    transaction_history.extend(user_transfers_out)
    transaction_history.extend(user_deposits)
    transaction_history.extend(user_cheques)
    transaction_history = tuple(map(lambda t: t[0], sorted(transaction_history, key=lambda t: t[1])))

    return templates.TemplateResponse(
        "card/index.html",
        await build_base_context(
            request,
            extra={
                "transaction_history": transaction_history
            },
        ),
    )
