from typing import Any

from fastapi import Request

from LyPayAPI.user.info import get as get_user_info
from LyPayAPI.user.settings.avatar import get as get_avatar


def _format_balance(balance: Any) -> str | None:
    if balance is None:
        return None
    try:
        value = int(balance)
    except Exception:
        return str(balance)
    return f"{value:,}".replace(",", " ") + " Тгр."


async def build_base_context(
    request: Request,
    *,
    active_tab: str | None = None,
    hide_header: bool = False,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ctx: dict[str, Any] = {"request": request, "active_tab": active_tab, "hide_header": hide_header}

    session_user = request.session.get("user")
    if session_user:
        ctx["user"] = session_user
        user_id = session_user.get("ID")

        try:
            user_info = await get_user_info(user_id)
            ctx["balance"] = _format_balance(user_info.get("balance"))
        except Exception:
            pass

    try:
        api_answer = await get_avatar(user_id)
        if api_answer is not None:
            avatar, updated = api_answer
            avatar_url = "/" + str(avatar).lstrip("/")
            ctx["my_avatar"] = avatar_url
        else:
            raise Exception
    except Exception as e:
        ctx["my_avatar"] = "/static/qingque.jpg"

    if extra:
        ctx.update(extra)
    return ctx
