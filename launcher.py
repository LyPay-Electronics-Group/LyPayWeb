from uvicorn import run
from server import app


run(app, host='localhost', port=12345)