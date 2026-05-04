from os import system, getenv
from platform import system as get_platform
from dotenv import load_dotenv

load_dotenv()


if get_platform() == "Windows":
    system(
        f"uvicorn server:app "
        "--no-access-log "
        f"--workers %NUMBER_OF_PROCESSORS% "
        f"--host {getenv('LYPAY_HOST')} "
        f"--port {getenv('LYPAY_PORT')}"
   )

elif get_platform() == "Linux":
    system(
        f"uvicorn server:app "
        "--no-access-log "
        f"--workers $(nproc) "
        f"--host {getenv('LYPAY_HOST')} "
        f"--port {getenv('LYPAY_PORT')}"
    )
