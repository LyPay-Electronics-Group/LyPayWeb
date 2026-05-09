from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from LyPayAPI.store.registration import check_link, get_ID, new, send_email
from LyPayAPI.admin.info import db_query

router = APIRouter()
templates = Jinja2Templates(directory="html/store")


@router.get("/register", response_class=HTMLResponse)
async def register_store_page(request: Request):
    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse(url="/login", status_code=303)
    # todo: проверка есть ли у юзера магаз
    await send_email("mandzhiev.ts@students.sch2.ru", "123")
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def check_store_code(
        request: Request,
        code: str = Form(...)
):
    user_info = request.session.get("user")
    email = user_info["email"]
    print(user_info)
    is_valid = await check_link(email, code)

    if not is_valid:
        return templates.TemplateResponse(
            "store_register.html",
            {"request": request, "error": "Неверный код", "user": user_info}
        )

    request.session["store"] = {
        "host_id": user_info["ID"]
    }

    return RedirectResponse(url="/store/register/select-id", status_code=303)


@router.get("/register/select-id", response_class=HTMLResponse)
async def select_store_id_page(request: Request):
    if "store" not in request.session:
        return RedirectResponse(url="/store/register", status_code=303)
    # todo: проверка есть ли у юзера магаз
    variants = [await get_ID() for _ in range(10)]

    return templates.TemplateResponse(
        "select_id.html",
        {"request": request, "variants": variants}
    )


@router.post("/register/select-id")
async def create_store(
        request: Request,
        store_id: str = Form(...),
        name: str = Form(...)
):
    reg_data = request.session.get("user")
    if not reg_data:
        return RedirectResponse(url="/store/register", status_code=303)
    request.session["store"]["ID"] = store_id
    request.session["store"]["name"] = name

    await new(
        storeID=store_id,
        email=reg_data["email"],
        name=name,
        hostID=reg_data["ID"]
    )

    return RedirectResponse(url="/profile", status_code=303)


@router.get("", response_class=HTMLResponse)
async def my_stores(request: Request):
    reg_data = request.session.get("store")  # todo: брать по id юзера
    if not reg_data:
        return RedirectResponse(url="/store/register", status_code=303)
    print(reg_data)
    return templates.TemplateResponse(
        "store.html",
        {"request": request, "store": reg_data}
    )
