from fastapi import APIRouter, Request, Depends as D, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.fps import status, pay
from LyPayAPI.__exceptions__ import IDNotFound

from scripts.firewall_validator import firewall_validate_factory as FVF
from scripts.base_context import build_base_context
from source.errors import to_user_message

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/fps", response_class=HTMLResponse)
async def fps_index(
        request: Request,
        message: str = None,
        firewall_ok=D(FVF('main'))
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "fps/index.html",
        await build_base_context(
            request,
            extra={"message": message} if message is not None else None
        ),
    )


@router.post("/fps")
async def redirect_to_pay_page(
        request: Request,
        ID = Form(...),
        firewall_ok=D(FVF('main'))
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user_info = request.session.get("user", None)
    if not user_info:
        return RedirectResponse(url="/login", status_code=303)

    try:
        ID = ID.strip().lower()
        valid = await status(ID)
        if valid is not None:
            return RedirectResponse(
                url=f"/fps/{ID}",
                status_code=303
            )
    except:
        pass
    return RedirectResponse(
        url="/fps?message=FPS-линк+с+таким+ID+не+найден!",
        status_code=303
    )


@router.get("/fps/{ID}")
async def fps_pay_page(
        request: Request,
        ID: str,
        firewall_ok=D(FVF('main'))
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user_info = request.session.get("user", None)
    if not user_info:
        return RedirectResponse(url="/login", status_code=303)

    try:
        return templates.TemplateResponse(
            "fps/fps.html",
            await build_base_context(
                request,
                extra={
                    "ID": ID,
                    "data": await status(ID)
                }
            ),
        )
    except IDNotFound:
        return RedirectResponse(
            url="/fps?message=FPS-линк+с+таким+ID+не+найден!",
            status_code=303
        )


@router.post("/fps/{ID}/pay")
async def fps_pay(
        request: Request,
        ID: str,
        firewall_ok=D(FVF('main'))
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user_info = request.session.get("user", None)
    if not user_info:
        return RedirectResponse(url="/login", status_code=303)

    try:
        link_status = await status(ID)
        print(link_status)
        if link_status["payed"] is None:
            await pay(ID, user_info["ID"])
        return RedirectResponse(url=f"/fps/{ID}", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            "fps/fps.html",
            await build_base_context(
                request,
                extra={
                    "ID": ID,
                    "data": await status(ID),
                    "error": to_user_message(e)
                }
            ),
        )
