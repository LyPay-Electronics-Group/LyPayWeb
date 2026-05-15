from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from scripts.base_context import build_base_context

from LyPayAPI.store.registration import check_link, get_ID, new, send_email
from LyPayAPI.store.info import get_all_shopkeepers
from LyPayAPI.user.info import get

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/", response_class=HTMLResponse)
async def register_store_page(request: Request):
    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse(url="/login", status_code=303)

    if user_info["ID"] in await get_all_shopkeepers():
        return RedirectResponse(url="/store", status_code=303)

    #await send_email("mandzhiev.ts@students.sch2.ru")  # TEMP
    request.session["store"] = {"registration": True}
    return templates.TemplateResponse("store/register.html", await build_base_context(request, active_tab="stores"))


@router.post("/")
async def check_store_code(request: Request, code: str = Form(...)):
    user_info = request.session.get("user")
    ID = user_info["ID"]
    user = await get(ID)
    email = user["email"]
    is_valid = await check_link(email, code)

    if not is_valid:
        return templates.TemplateResponse(
            "store/register.html",
            await build_base_context(
                request,
                active_tab="stores",
                extra={"error": "Неверный код", "user": user_info},
            ),
        )

    request.session["store"]["host_id"] = user_info["ID"]
    return RedirectResponse(url="/store/register/select-id", status_code=303)


@router.get("/select-id", response_class=HTMLResponse)
async def select_store_id_page(request: Request):
    if "store" not in request.session or not request.session["store"].get("registration", False):
        return RedirectResponse(url="/store/register", status_code=303)

    variants = [await get_ID() for _ in range(10)]
    return templates.TemplateResponse(
        "store/select_id.html",
        await build_base_context(request, active_tab="stores", extra={"variants": variants}),
    )


@router.post("/select-id")
async def create_store(request: Request, store_id: str = Form(...), name: str = Form(...)):
    user_info = request.session.get("user")
    if user_info is None:
        return RedirectResponse(url="/login", status_code=303)
    ID = user_info["ID"]
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

    return RedirectResponse(url="/store", status_code=303)
