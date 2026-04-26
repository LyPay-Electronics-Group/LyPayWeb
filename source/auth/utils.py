from LyPayAPI.user.registration import check_email_record, send_email, new
from LyPayAPI.user.info import get_by_email
from LyPayAPI.__exceptions__ import APIError


async def send_verification_code(email: str, code: str) -> None:
    """
    Проверяет, не занят ли email, и отправляет на него код подтверждения.
    """
    await check_email_record(email)
    await send_email(route="main", participant=email, code=code)


async def verify_code(email: str, code: str, ref_code: str) -> bool:
    """
    Проверяет код подтверждения для указанного email.
    """
    if code == ref_code:
        return True
    raise APIError()  # todo: выдать ошибку


async def register_user(email: str, password: str, login: str):
    """
    Регистрирует нового пользователя через LyPayAPI.
    Возвращает ID созданного пользователя или выбрасывает исключение APIError.
    """
    user_info = await check_email_record(email)
    print(user_info)
    user_id = await new(
        email=email,
        login=login,
        password=password,
        name=user_info["name"],
        group=user_info["group"],
        owner_flag="web_owner"
    )
    return user_id


async def authenticate_user(email: str, password: str):
    """
    Проверяет учётные данные пользователя.
    """
    user_data = await get_by_email(email)
    print(user_data)
    if user_data and user_data.get("password") == password:
        return user_data
    return None
