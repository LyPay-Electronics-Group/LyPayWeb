from LyPayAPI.user.registration import check_email_record, send_email, new, check_code
from LyPayAPI.user.info import get_by_email, get_by_login
from LyPayAPI.__exceptions__ import APIError, EmailNotFound, IDAlreadyExists


async def send_verification_code(email: str) -> dict[str, ...]:
    """
    Проверяет, что email ещё не зарегистрирован, и отправляет на него код подтверждения.
    Возвращает corp_record.
    """
    corp_record = await check_email_record(email)

    try:
        existing_user = await get_by_email(email)
    except EmailNotFound:
        existing_user = None

    if existing_user:
        raise IDAlreadyExists

    await send_email(route="main", participant=email)
    return corp_record


async def verify_code(email: str, code: str) -> bool:
    """
    Проверяет код подтверждения для указанного email.
    """
    try:
        return await check_code(email, code)
    except APIError:
        return False


async def register_user(
        email: str,
        password: str,
        login: str,
        name: str,
        group: str
):
    """
    Регистрирует нового пользователя через LyPayAPI и возвращает ID созданного пользователя.
    """
    user_id = await new(
        email=email,
        login=login,
        password=password,
        name=name,
        group=group,
        owner_flag="web_owner",
    )
    return user_id


async def authenticate_user(identifier: str, password: str):
    """
    Проверяет учётные данные пользователя по email или логину.
    Возвращает user_data или None.
    """
    try:
        user_data = await get_by_email(identifier)
    except APIError:
        try:
            user_data = await get_by_login(identifier)
        except APIError:
            return None

    if user_data and user_data.get("password") == password:
        return user_data
    return None
