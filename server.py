from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import FileResponse

from source.test import router as test_router
from source.auth import router as auth_router
from source.mst import router as mst_router

from logging import getLogger, StreamHandler
from sys import stdout
from middleware.logger import CustomLog

app = FastAPI()

logger = getLogger("app.requests")
logger.setLevel(20)  # level INFO
logger.addHandler(StreamHandler(stdout))

app.add_middleware(CustomLog, app_logger=logger, blacklist=[
    "/mst/machine/local_stats",
    "/mst/machine/core_stats"
])
app.add_middleware(SessionMiddleware, secret_key="verysecretkey")  # todo:брать из .env

app.include_router(test_router)
app.include_router(auth_router)
app.include_router(mst_router, prefix='/mst')

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return "LyPay Forever!"


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")
