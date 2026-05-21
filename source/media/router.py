from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

STORES_AVATAR_DIR = Path("media/stores_media")
STORES_AVATAR_DIR.mkdir(parents=True, exist_ok=True)

USERS_AVATAR_DIR = Path("media/users_media")
USERS_AVATAR_DIR.mkdir(parents=True, exist_ok=True)

QR_DIR = Path("media/users_qr")
QR_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/media/stores_media/{filename}")
async def serve_store_avatar(filename: str, request: Request):
    user = request.session.get("user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    file_path = STORES_AVATAR_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path, media_type="image/jpeg", headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })


@router.get("/media/users_media/{filename}")
async def serve_avatar(filename: str, request: Request):
    user = request.session.get("user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    file_path = USERS_AVATAR_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path, media_type="image/jpeg", headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })


@router.get("/media/users_qr/{filename}")
async def serve_avatar(filename: str, request: Request):
    user = request.session.get("user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    file_path = QR_DIR / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(file_path, media_type="image/jpeg", headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })
