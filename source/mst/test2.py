import time
import asyncio
from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from LyPayAPI.mst.test2 import main

router = APIRouter()
templates = Jinja2Templates(directory="html/mst")


@router.get("/test2")
async def test2_page(request: Request):
    return templates.TemplateResponse("test2.html", {"request": request})


@router.post("/test2/run")
async def run_test2(count: int = Form(..., ge=1, le=5000)):
    total_time = 0
    lost = 0

    for _ in range(count):
        start = time.perf_counter()
        try:
            data = await main()
            elapsed = time.perf_counter() - start
            if isinstance(data, bytes) and len(data) == 1024 * 1024:
                total_time += elapsed
            else:
                lost += 1
        except Exception as e:
            lost += 1
            print(e)

    avg_time = total_time / (count - lost) if (count - lost) else 0.0
    loss_percent = (lost / count) * 100 if count > 0 else 0.0

    return JSONResponse(content={
        "total": count,
        "success": count - lost,
        "lost": lost,
        "loss_percent": round(loss_percent, 2),
        "avg_time_ms": round(avg_time * 1000, 3)
    })
