from fastapi import APIRouter, Request, Depends as D, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from pathlib import Path

from scripts.firewall_validator import firewall_validate_factory as FVF
from scripts.base_context import build_base_context

from LyPayAPI.store.info import get as get_store, get_by_shopkeeper
from LyPayAPI.store.settings.name import update as update_name
from LyPayAPI.store.settings.description import update as update_description
from LyPayAPI.store.settings.avatar import update as update_avatar, get as get_avatar
from LyPayAPI.utils.format import clear

router = APIRouter()
templates = Jinja2Templates(directory="html")

AVATAR_DIR = Path("media/stores_media")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

AVATAR_MAX_SIZE = 5 * 1024 * 1024


async def _require_host_store(request: Request) -> tuple[dict, str, dict]:
    user_info = request.session.get("user")
    if not user_info:
        raise HTTPException(status_code=401, detail="auth required")

    store_id = await get_by_shopkeeper(user_info["ID"])
    store = await get_store(store_id)
    if store.get("hostID") != user_info["ID"]:
        raise HTTPException(status_code=403, detail="host required")

    return user_info, store_id, store


@router.get("/", response_class=HTMLResponse)
async def settings_page(
        request: Request,
        firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    try:
        _, store_id, store = await _require_host_store(request)
    except HTTPException as e:
        if e.status_code in (401, 403):
            return RedirectResponse("/store", status_code=303)
        raise

    try:
        api_answer = await get_avatar(store_id)
        if api_answer is not None:
            avatar_path, _ = api_answer
            avatar_url = '/' + avatar_path
        else:
            raise Exception
    except Exception:
        avatar_url = "/static/qingque.jpg"

    message = request.query_params.get("message")
    error = request.query_params.get("error")

    return templates.TemplateResponse(
        "store/settings.html",
        await build_base_context(
            request,
            extra={
                "store": store,
                "avatar": avatar_url,
                "message": message,
                "error": error,
            },
        ),
    )


@router.post("/save")
async def save_settings(
        request: Request,
        name: str = Form(...),
        description: str = Form(...),
        firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    try:
        _, store_id, _ = await _require_host_store(request)
    except HTTPException as e:
        if e.status_code in (401, 403):
            return RedirectResponse("/store", status_code=303)
        raise

    try:
        await update_name(store_id, clear(name))
        await update_description(store_id, clear(description))
    except Exception as e:
        return RedirectResponse(
            url="/store/settings?error=Не+удалось+сохранить",
            status_code=303,
        )

    return RedirectResponse(
        url="/store/settings?message=Сохранено",
        status_code=303,
    )


@router.post("/avatar")
async def upload_store_avatar(
        request: Request,
        file: UploadFile = File(...),
        firewall_ok=D(FVF("stores")),
):
    if not firewall_ok:
        return RedirectResponse("/", status_code=303)

    try:
        _, store_id, _ = await _require_host_store(request)
    except HTTPException as e:
        if e.status_code in (401, 403):
            return RedirectResponse("/store", status_code=303)
        raise

    if not file.content_type or not file.content_type.startswith("image/"):
        return RedirectResponse(
            url="/store/settings?error=Прикрепите+картинку",
            status_code=303,
        )
    if file.size > AVATAR_MAX_SIZE:
        return RedirectResponse(
            url="/store/settings?error=Слишком большой размер файла",
            status_code=303
        )

    file_path = AVATAR_DIR / f"tmp_{store_id}.jpg"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        await update_avatar(store_id, str(file_path))
    finally:
        if file_path.exists():
            file_path.unlink()

    return RedirectResponse(
        url="/store/settings?message=Аватар+обновлён",
        status_code=303,
    )
