from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .utils import register_user, authenticate_user

router = APIRouter()
templates = Jinja2Templates(directory="html")


# --- Страница входа ---
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = await authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный email или пароль."
        }, status_code=401)
    request.session["user"] = {"ID": user["ID"], "email": user["email"]}
    return RedirectResponse(url="/dashboard", status_code=303)


# --- Страница регистрации ---
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        login: str = Form(...)
):
    try:
        user_id = await register_user(email, password, login)
        request.session["user"] = {"ID": user_id, "email": email}
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e)
        }, status_code=400)


# --- Выход ---
@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/login")