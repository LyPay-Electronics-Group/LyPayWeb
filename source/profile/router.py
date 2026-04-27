from pathlib import Path

from fastapi import APIRouter, Request
from fastapi import UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.user.info import get
from LyPayAPI.user.settings.avatar import update as update_avatar, get as get_avatar

router = APIRouter()
templates = Jinja2Templates(directory="html")

AVATAR_DIR = Path("static/avatars")
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
        print('api answer:', api_answer)
        if api_answer is not None:
            avatar, updated = api_answer
            print('avatar:', avatar)
        else:
            raise Exception
    except Exception as e:
        avatar = "/static/avatars/default.jpg"
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
    file_path = AVATAR_DIR / f"{user_id}.jpg"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    print(user_id)
    await update_avatar(user_id, str(file_path))
    return RedirectResponse(
        url="/profile?message=Аватар+обновлён",
        status_code=303
    )
