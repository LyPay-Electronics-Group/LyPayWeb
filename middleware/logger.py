from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from logging import Logger
from http import HTTPStatus

from colorama import Fore, Style, init as c_init

c_init(autoreset=True)


class CustomLog(BaseHTTPMiddleware):
    max_client_length = 15
    max_id_length = 8
    max_message_length = 96

    def __init__(self, app: ASGIApp, app_logger: Logger, blacklist: tuple[str]):
        super().__init__(app)
        self.app_logger = app_logger
        self.blacklist = blacklist


    async def dispatch(self, request, call_next):
        response = await call_next(request)

        if request.url.path not in self.blacklist:
            client = f"{request.client.host}"
            client_id = str(request.session.get("user", {"ID": '<null>'})["ID"])
            message = Fore.GREEN + Style.NORMAL + f"{request.method}" + \
            (' ' if request.method == "GET" else '') + \
            Fore.CYAN + Style.NORMAL + f" {request.url.path}" + Style.RESET_ALL

            self.app_logger.info(
                Fore.LIGHTBLACK_EX + Style.BRIGHT + client + Style.RESET_ALL +
                " " * max(self.max_client_length - len(client), 0) +
                " | " + Fore.CYAN + Style.BRIGHT + client_id + Style.RESET_ALL +
                " " * max(self.max_id_length - len(client_id), 0) +
                " | " + message + " " * max(self.max_message_length - len(message) - 5, 0) + " | " +
                (Fore.RED if response.status_code >= 400 else (Fore.YELLOW if response.status_code >= 300 else Fore.GREEN)) +
                f"{response.status_code} {HTTPStatus(response.status_code).phrase}" + Style.RESET_ALL
            )

        return response
