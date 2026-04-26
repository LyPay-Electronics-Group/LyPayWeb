from uvicorn import run
from server import app


run(app, host='26.251.171.35', port=12345)