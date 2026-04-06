from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="html")


@router.get("/qq", response_class=HTMLResponse)
async def QQ_skill_issue(request: Request):
    return templates.TemplateResponse(name="test.html", request=request)
