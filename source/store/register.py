from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from scripts.base_context import build_base_context

from LyPayAPI.store.registration import check_link, get_ID, new
from LyPayAPI.store.info import get_all_shopkeepers
from LyPayAPI.user.info import get
from LyPayAPI.utils.settings import get as get_setting
from source.errors import is_bad_firewall_error, to_user_message

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/", response_class=HTMLResponse)
async def register_store_page(request: Request):
    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse(url="/login?redirect=store", status_code=303)

    if not await get_setting("store_can_register"):
        return RedirectResponse(url="/", status_code=303)

    try:
        if user_info["ID"] in await get_all_shopkeepers():
            return RedirectResponse(url="/store/", status_code=303)
    except Exception as e:
        if is_bad_firewall_error(e):
            return RedirectResponse(url="/bad-firewall-status", status_code=303)
        return templates.TemplateResponse(
            "store/register.html",
            await build_base_context(request, extra={"error": to_user_message(e)}),
            status_code=503,
        )

    request.session["store"] = {"registration": True}
    return templates.TemplateResponse("store/register.html", await build_base_context(request))


@router.post("/")
async def check_store_code(request: Request, code: str = Form(...)):
    user_info = request.session.get("user")
    if user_info is None:
        return RedirectResponse(url="/login?redirect=store", status_code=303)

    try:
        link_email = await check_link(code)
    except Exception as e:
        if is_bad_firewall_error(e):
            return RedirectResponse(url="/bad-firewall-status", status_code=303)
        return templates.TemplateResponse(
            "store/register.html",
            await build_base_context(request, extra={"error": to_user_message(e), "user": user_info}),
            status_code=400,
        )

    if not link_email:
        return templates.TemplateResponse(
            "store/register.html",
            await build_base_context(
                request,
                active_tab="stores",
                extra={"error": "Неверный код", "user": user_info},
            ),
        )

    request.session.setdefault("store", {})["host_id"] = user_info["ID"]
    request.session["store"]["registration"] = True
    return RedirectResponse(url="/store/register/select-id", status_code=303)


@router.get("/select-id", response_class=HTMLResponse)
async def select_store_id_page(request: Request):
    if "store" not in request.session or not request.session["store"].get("registration", False):
        return RedirectResponse(url="/store/register", status_code=303)

    try:
        variants = [await get_ID() for _ in range(10)]
    except Exception as e:
        if is_bad_firewall_error(e):
            return RedirectResponse(url="/bad-firewall-status", status_code=303)
        return templates.TemplateResponse(
            "store/register.html",
            await build_base_context(request, extra={"error": to_user_message(e)}),
            status_code=503,
        )
    return templates.TemplateResponse(
        "store/select_id.html",
        await build_base_context(request, extra={"variants": variants}),
    )


@router.post("/select-id")
async def create_store(request: Request, store_id: str = Form(...), name: str = Form(...)):
    user_info = request.session.get("user")
    if user_info is None:
        return RedirectResponse(url="/login?redirect=store", status_code=303)
    if "store" not in request.session or not request.session["store"].get("registration", False):
        return RedirectResponse(url="/store/register", status_code=303)
    ID = user_info["ID"]
    try:
        user = await get(ID)
        email = user["email"]
        request.session["store"]["ID"] = store_id
        request.session["store"]["name"] = name

        await new(
            storeID=store_id,
            email=email,
            name=name,
            hostID=ID,
        )
    except Exception as e:
        if is_bad_firewall_error(e):
            return RedirectResponse(url="/bad-firewall-status", status_code=303)

        try:
            variants = [await get_ID() for _ in range(10)]
        except Exception:
            variants = [store_id]

        return templates.TemplateResponse(
            "store/select_id.html",
            await build_base_context(
                request,
                active_tab="stores",
                extra={
                    "variants": variants,
                    "error": to_user_message(e),
                    "selected_store_id": store_id,
                    "store_name": name,
                },
            ),
            status_code=400,
        )

    request.session.pop("store", None)
    return RedirectResponse(url="/store/", status_code=303)
