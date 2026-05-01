from fastapi import APIRouter, Request, Form, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from scripts.unix import unix

from LyPayAPI.mst.test2 import main
from hashlib import sha256

router = APIRouter()
templates = Jinja2Templates(directory="html/mst")

GLOBAL_TEST2_STORAGE = dict()


@router.get("/test2")
async def test2_page(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)
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

    current_count = websocket.session["mst"]["test2"]["count"]
    current_ID = websocket.session["user"]["ID"]
    await websocket.send_text(str(current_count))

    if GLOBAL_TEST2_STORAGE.get(current_ID) is None:
        GLOBAL_TEST2_STORAGE[current_ID] = {
            "time": 0,
            "total": 0,
            "success": 0
        }
    print(GLOBAL_TEST2_STORAGE)
    for _ in range(websocket.session["mst"]["test2"]["count"]):
        data = await main()

        start_time = unix()
        await websocket.send_bytes(data)
        client_hash = await websocket.receive_text()
        end_time = unix()

        GLOBAL_TEST2_STORAGE[current_ID]["time"] += end_time - start_time
        GLOBAL_TEST2_STORAGE[current_ID]["total"] += 1
        if client_hash == sha256(data).hexdigest():
            GLOBAL_TEST2_STORAGE[current_ID]["success"] += 1

    print(GLOBAL_TEST2_STORAGE)
    await websocket.close()


@router.post("/test2/end")
async def end_test2(request: Request):
    if request.session.get("user") is None:
        return RedirectResponse(url="/login", status_code=303)

    if request.session.get("mst") is not None and request.session.get("mst").get("test2") is not None:
        request.session["mst"]["test2"] = GLOBAL_TEST2_STORAGE[request.session["user"]["ID"]]
    return {"status": "ok"}
