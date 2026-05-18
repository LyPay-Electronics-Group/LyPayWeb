from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from scripts.base_context import build_base_context

router = APIRouter()
templates = Jinja2Templates(directory="html")


async def base(request: Request):
    user_info = request.session.get("user")
    if not user_info:
        return RedirectResponse("/login", status_code=303)

    return templates.TemplateResponse(
        "plug.html",
        await build_base_context(request),
    )


@router.get("/stores", response_class=HTMLResponse)
async def store(request: Request):
    return await base(request)


@router.get("/transfer", response_class=HTMLResponse)
async def transfer(request: Request):
    return await base(request)
