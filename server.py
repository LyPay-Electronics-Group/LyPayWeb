from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from source.test import router as test_router


app = FastAPI()
app.include_router(test_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return "LyPay Forever!"
