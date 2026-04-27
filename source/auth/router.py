from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .utils import register_user, authenticate_user, send_verification_code, verify_code

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
    code_sent = request.session.get("registration_code_sent", False)
    email = request.session.get("registration_email", "")
    return templates.TemplateResponse("register.html", {
        "request": request,
        "code_sent": code_sent,
        "email": email,
        "error": None
    })


@router.post("/register/send-code")
async def register_send_code(request: Request, email: str = Form(...)):
    try:
        await send_verification_code(email)
        request.session["registration_email"] = email
        request.session["registration_code_sent"] = True
        request.session["registration_code_verified"] = False
        return RedirectResponse(url="/register", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "email": email,
            "code_sent": False,
            "error": str(e)
        }, status_code=400)


@router.post("/register/verify")
async def register_verify(
        request: Request,
        code: str = Form(...),
        password: str = Form(...),
        login: str = Form(...)
):
    email = request.session.get("registration_email")
    if not email:
        return RedirectResponse(url="/register", status_code=303)

    try:
        if not await verify_code(email, code):
            raise ValueError("Неверный код.")
        user_id = await register_user(email, password, login)
        request.session.pop("registration_email", None)
        request.session.pop("registration_code_sent", None)
        request.session.pop("registration_code_verified", None)
        request.session["user"] = {"ID": user_id, "email": email}
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "email": email,
            "code_sent": True,
            "error": str(e)
        }, status_code=400)


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


@router.get("/dashboard")
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    return HTMLResponse(f"<h1>Добро пожаловать, {user['email']}!</h1><a href='/logout'>Выйти</a>")
