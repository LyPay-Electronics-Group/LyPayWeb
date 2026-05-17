from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

AVATAR_DIR = Path("media/stores_media")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/media/stores_media/{filename}")
async def serve_store_avatar(filename: str, request: Request):
    file_path = AVATAR_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path, media_type="image/jpeg")


@router.get("/media/users_media/{filename}")
async def serve_avatar(filename: str, request: Request):
    user = request.session.get("user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    file_path = AVATAR_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path, media_type="image/jpeg")
