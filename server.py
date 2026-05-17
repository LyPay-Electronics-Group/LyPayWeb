from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from source.test import router as test_router
from source.auth import router as auth_router
#from source.mst import router as mst_router
from source.store import router as store_router
from source.profile import router as profile_router
from source.media import router as media_router

from scripts.base_context import build_base_context

from logging import getLogger, StreamHandler
from sys import stdout
from middleware.logger import CustomLog
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

logger = getLogger("app.requests")
logger.setLevel(20)  # level INFO
logger.addHandler(StreamHandler(stdout))

app.add_middleware(CustomLog, app_logger=logger, blacklist=(
    "/mst/machine/local_stats",
    "/mst/machine/core_stats"
))
app.add_middleware(SessionMiddleware, secret_key="verysecretkey")  # todo:брать из .env

app.include_router(test_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(media_router)
app.include_router(store_router, prefix="/store")
#app.include_router(mst_router, prefix='/mst')

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="html")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", await build_base_context(request, active_tab="home"))


@app.get("/bad-firewall-status", response_class=HTMLResponse, include_in_schema=False)
async def bad_firewall_status(request: Request):
    return templates.TemplateResponse(
        "errors/bad_firewall_status.html",
        await build_base_context(request),
        status_code=403,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> Response:
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "errors/404.html",
            await build_base_context(request),
            status_code=404,
        )

    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")
