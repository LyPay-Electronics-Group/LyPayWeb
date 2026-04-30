from fastapi import APIRouter, Request, Form, WebSocket
from fastapi.templating import Jinja2Templates

from scripts.unix import unix

from LyPayAPI.mst.test2 import main
from hashlib import sha256

router = APIRouter()
templates = Jinja2Templates(directory="html/mst")


@router.get("/test2")
async def test2_page(request: Request):
    return templates.TemplateResponse("test2.html", {"request": request})


@router.post("/test2/configure")
async def configure_test2(request: Request, count: int = Form(...)):
    if request.session.get("mst") is None:
        request.session["mst"] = dict()
    if request.session["mst"].get("test2") is None:
        request.session["mst"]["test2"] = {
            "count": count,
            "time": 0,
            "total": 0,
            "success": 0
        }
    else:
        request.session["mst"]["test2"]["count"] = count


@router.websocket("/test2/run")
async def run_test2(websocket: WebSocket):
    await websocket.accept()

    await websocket.send_text(str(websocket.session["mst"]["test2"]["count"]))
    for _ in range(websocket.session["mst"]["test2"]["count"]):
        data = await main()

        start_time = unix()
        await websocket.send_bytes(data)
        client_hash = await websocket.receive_text()
        end_time = unix()

        websocket.session["mst"]["test2"]["time"] += end_time - start_time
        websocket.session["mst"]["test2"]["total"] += 1
        if client_hash == sha256(data).hexdigest():
            websocket.session["mst"]["test2"]["success"] += 1

    await websocket.close()
