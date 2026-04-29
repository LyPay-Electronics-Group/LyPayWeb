from pathlib import Path

from fastapi import APIRouter, Request, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.user.info import get
from LyPayAPI.user.settings.avatar import update as update_avatar, get as get_avatar

router = APIRouter()
templates = Jinja2Templates(directory="html")

AVATAR_DIR = Path("media/users_media")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


# --- Страница профиля ---
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse(url="/login", status_code=303)
    print(user_info)
    user_id = user_info["ID"]
    try:
        user_info = await get(user_id)
    except Exception as e:
        return HTMLResponse(content=f"Ошибка: {str(e)}", status_code=500)
    try:
        api_answer = await get_avatar(user_id)
        if api_answer is not None:
            avatar, updated = api_answer
        else:
            raise Exception
    except Exception as e:
        avatar = "/static/skill_issue.jpg"
        print(e)
    print(avatar)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user_info,
        "avatar": avatar
    })


@router.post("/profile/avatar")
async def upload_avatar(
        request: Request,
        file: UploadFile = File(...)
):
    user_info = request.session.get("user")
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
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    try:
        file_user_id = int(filename.rsplit(".", 1)[0])
    except (ValueError, IndexError):
        raise HTTPException(status_code=403, detail="Неверный формат файла")

    if file_user_id != user["ID"]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    file_path = AVATAR_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path, media_type="image/jpeg")
