from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends as D
from fastapi import UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from scripts.firewall_validator import firewall_validate_factory as FVF

from LyPayAPI.user.info import get
from LyPayAPI.user.settings.avatar import update as update_avatar, get as get_avatar
from LyPayAPI.__exceptions__ import IDNotFound
from scripts.base_context import build_base_context

router = APIRouter()
templates = Jinja2Templates(directory="html")

AVATAR_DIR = Path("media/users_media")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/profile", response_class=HTMLResponse)
async def profile_page_redirect(
        request: Request,
        firewall_ok = D(FVF('main'))
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse(url="/login", status_code=303)

    return RedirectResponse(url=f"/profile/{user_info["ID"]}", status_code=303)


@router.get("/profile/{ID}", response_class=HTMLResponse)
async def profile_page(
        ID: int,
        request: Request,
        firewall_ok = D(FVF('main'))
):
    if not firewall_ok:
        return RedirectResponse(url="/bad-firewall-status", status_code=303)

    user_info = request.session.get("user", None)
    if user_info is None:
        return RedirectResponse(url="/login", status_code=303)
    user_id = user_info["ID"]

    try:
        user_info = await get(user_id)
        requested_profile = await get(ID)
    except IDNotFound:
        return RedirectResponse(url="/profile", status_code=303)
    except Exception as e:
        return HTMLResponse(content=f"Ошибка: {str(e)}", status_code=500)

    clean_user_info = {
        "ID":     requested_profile["ID"],
        "Логин":  requested_profile["login"],
        "Имя":    requested_profile["name"],
        "Группа": requested_profile["group"],
        "Почта":  requested_profile["email"]
    }
    if ID == user_id:
        clean_user_info["Баланс"] = user_info["balance"]

    try:
        api_answer = await get_avatar(ID)
        if api_answer is not None:
            avatar, updated = api_answer
            avatar = '/' + avatar
        else:
            raise Exception
    except Exception as e:
        avatar = "/static/skill_issue.jpg"

    return templates.TemplateResponse(
        "profile/profile.html",
        await build_base_context(
            request,
            active_tab="menu",
            extra={
                "user": clean_user_info,
                "avatar": avatar,
                "is_self": ID == user_id,
            },
        ),
    )


@router.post("/profile/avatar")
async def upload_avatar(
        request: Request,
        file: UploadFile = File(...)
):
    user_info = request.session.get("user", None)
    if not user_info:
        return RedirectResponse(url="/login", status_code=303)
    if file.content_type[:5] != "image":
        return RedirectResponse(
            url="/profile?error=Прикрепите+картинку",
            status_code=303
        )
    user_id = user_info["ID"]
    file_path = AVATAR_DIR / f"tmp_{user_id}.jpg"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    await update_avatar(user_id, str(file_path))
    file_path.unlink()
    return RedirectResponse(
        url="/profile?message=Аватар+обновлён",
        status_code=303
    )


@router.get("/media/users_media/{filename}")
async def serve_avatar(filename: str, request: Request):
    user = request.session.get("user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    file_path = AVATAR_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path, media_type="image/jpeg")
