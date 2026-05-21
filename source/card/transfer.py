from fastapi import APIRouter, Request, Depends as D, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.user import transactions

from scripts.base_context import build_base_context
from scripts.firewall_validator import firewall_validate_factory as FVF

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/card/transfer", response_class=HTMLResponse)
async def transfer_page(
    request: Request,
    ok: int | None = None,
    err: str | None = None,
    firewall_ok=D(FVF("main")),
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "card/transfer.html",
        await build_base_context(
            request,
            active_tab="card",
            extra={"ok": bool(ok), "err": err},
        ),
    )


@router.post("/card/transfer", response_class=HTMLResponse)
async def transfer_submit(
    request: Request,
    id_in: str = Form(...),
    amount: str = Form(...),
    firewall_ok=D(FVF("main")),
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse("/login", status_code=303)

    id_in = (id_in or "").strip()
    amount = (amount or "").strip()

    try:
        id_in_int = int(id_in)
        amount_int = int(amount)
        if id_in_int == int(user_info["ID"]):
            return RedirectResponse("/card/transfer?err=Нельзя+перевести+самому+себе", status_code=303)
    except Exception:
        return RedirectResponse("/card/transfer?err=Проверь+ID+и+сумму", status_code=303)

    try:
        await transactions.transfer(int(user_info["ID"]), id_in_int, amount_int)
    except Exception as e:
        return RedirectResponse("/card/transfer?err=Не+удалось+выполнить+перевод", status_code=303)

    return RedirectResponse("/card/transfer?ok=1", status_code=303)

