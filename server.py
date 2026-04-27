from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from source.test import router as test_router
from source.auth import router as auth_router
from source.profile import router as profile_router

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="verysecretkey")  # todo:брать из .env
app.include_router(test_router)
app.include_router(auth_router)
app.include_router(profile_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return "LyPay Forever!"
