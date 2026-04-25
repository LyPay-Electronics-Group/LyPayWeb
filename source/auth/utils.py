from LyPayAPI.user.registration import check_email_record, send_email, new
from LyPayAPI.user.info import get_by_email


async def register_user(email: str, password: str, login: str):
    """
    Регистрирует нового пользователя через LyPayAPI.
    Возвращает ID созданного пользователя или выбрасывает исключение APIError.
    """
    user_info = await check_email_record(email)
    print(user_info)
    code = "123"  # todo:сделать проверку почты
    await send_email(route="main", participant=email, code=code)

    # Создаём пользователя
    user_id = await new(
        email=email,
        login=login,
        password=password,
        name=user_info["name"],
        group=user_info["class"],
        owner_flag="web_owner"
    )
    print(user_id)
    return user_id


async def authenticate_user(email: str, password: str):
    """
    Проверяет учётные данные пользователя.
    Так как прямого метода /login в API нет, мы получаем информацию о пользователе
    по email (предполагается, что email уникален) и сверяем пароль.
    В реальном API нужно добавить конечную точку аутентификации.
    """
    user_data = await get_by_email(email)
    print(user_data)
    if user_data and user_data.get("password") == password:
        return user_data
    return None
