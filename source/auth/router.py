from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .utils import authenticate_user, register_user, send_verification_code, verify_code

router = APIRouter()
templates = Jinja2Templates(directory="html")


def _clear_registration_session(request: Request) -> None:
    request.session.pop("registration_email", None)
    request.session.pop("registration_code_sent", None)
    request.session.pop("registration_corp_record", None)


def _registration_template(
        request: Request,
        *,
        email: str = "",
        code_sent: bool = False,
        error: Exception | None = None,
        status_code: int = 200,
):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "code_sent": code_sent,
            "email": email,
            "error": error,
        },
        status_code=status_code,
    )


# --- Страница входа ---
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/profile", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    identifier = email.strip()
    user = await authenticate_user(identifier, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный логин/email или пароль."},
            status_code=401,
        )
    request.session["user"] = {"ID": user["ID"], "email": user["email"]}
    return RedirectResponse(url="/profile", status_code=303)


# --- Страница регистрации ---
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/profile", status_code=303)

    code_sent = bool(request.session.get("registration_code_sent", False))
    email = request.session.get("registration_email", "")
    if code_sent and not email:
        _clear_registration_session(request)
        code_sent = False

    return _registration_template(request, email=email, code_sent=code_sent)


@router.post("/register/send-code")
async def register_send_code(request: Request, email: str = Form(...)):
    candidate_email = email.strip()
    _clear_registration_session(request)

    try:
        corp_record = await send_verification_code(candidate_email)
    except Exception as e:
        return _registration_template(
            request,
            email=candidate_email,
            code_sent=False,
            error=e,
            status_code=400,
        )

    request.session["registration_email"] = candidate_email
    request.session["registration_code_sent"] = True
    request.session["registration_corp_record"] = {
        "name": corp_record.get("name"),
        "group": corp_record.get("group"),
    }
    return RedirectResponse(url="/register", status_code=303)


@router.post("/register/verify")
async def register_verify(
        request: Request,
        code: str = Form(...),
        password: str = Form(...),
        login: str = Form(...),
):
    email = request.session.get("registration_email")
    code_sent = bool(request.session.get("registration_code_sent", False))
    if not email or not code_sent:
        _clear_registration_session(request)
        return RedirectResponse(url="/register", status_code=303)

    try:
        if not await verify_code(email, code):
            raise ValueError("Неверный код.")

        corp_record = request.session.get("registration_corp_record")
        name = corp_record.get("name")
        group = corp_record.get("group")

        user_id = await register_user(email, password, login, name=name, group=group)
        _clear_registration_session(request)
        request.session["user"] = {"ID": user_id, "email": email}
        return RedirectResponse(url="/profile", status_code=303)
    except Exception as e:
        return _registration_template(
            request,
            email=email,
            code_sent=True,
            error=e,
            status_code=400,
        )



# --- Выход ---
@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/login", status_code=303)

