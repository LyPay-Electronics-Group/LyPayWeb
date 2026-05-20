from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from scripts.base_context import build_base_context

from .utils import authenticate_user

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, redirect: str = None):
    if request.session.get("user"):
        if redirect == "store":
            return RedirectResponse(url="/store/register", status_code=303)
        return RedirectResponse(url="/profile", status_code=303)
    request.session["after_login_redirect"] = redirect
    return templates.TemplateResponse("auth/login.html", await build_base_context(request, hide_header=True))


@router.post("/login")
async def login(request: Request, identifier: str = Form(...), password: str = Form(...)):
    user = await authenticate_user(identifier.strip(), password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            await build_base_context(
                request,
                hide_header=True,
                extra={"error": "Неверный логин/email или пароль."},
            ),
            status_code=401,
        )
    request.session["user"] = {"ID": user["ID"], "email": user["email"]}

    if request.session.pop("after_login_redirect", None) == "store":
        return RedirectResponse(url="/store/register", status_code=303)
    return RedirectResponse(url="/profile", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=303)
