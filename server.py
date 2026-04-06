from fastapi import FastAPI

# from source.test import router as test_router


app = FastAPI()
# app.include_router(test_router)


@app.get("/")
async def root():
    return "LyPay Forever!"
