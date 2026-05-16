from LyPayAPI.__exceptions__ import (
    APIError,
    BadFireWallCheck,
    BadRequest,
    DBReturnedAVoid,
    EmailNotFound,
    IDAlreadyExists,
    IDNotFound,
    InvalidStoreDescription,
    InvalidStoreName,
    InvalidUserLogin,
    InvalidUserName,
    MediaNotFound,
    NoPythonProcessesFound,
    NotEnoughBalance,
    RegistrationEmailNotFound,
    SubZeroInput,
    UserIsAlreadyAShopkeeper,
)


def is_bad_firewall_error(exc: Exception) -> bool:
    return isinstance(exc, BadFireWallCheck)


def to_user_message(exc: Exception) -> str:
    if isinstance(exc, str):
        return exc

    if isinstance(exc, ValueError):
        message = str(exc).strip()
        return message if message else "Некорректные данные."

    if isinstance(exc, BadFireWallCheck):
        return "Запрос не прошёл проверку фаерволла. Попробуйте позже или смените сеть."

    if isinstance(exc, UserIsAlreadyAShopkeeper):
        return "Вы уже являетесь владельцем (или админом) магазина."

    if isinstance(exc, IDAlreadyExists):
        return "Такие данные уже используются. Попробуйте другие."

    if isinstance(exc, (InvalidUserLogin, InvalidUserName)):
        return "Данные не прошли проверку. Проверьте логин/имя и попробуйте снова."

    if isinstance(exc, (InvalidStoreName, InvalidStoreDescription)):
        return "Название/описание магазина не прошло проверку. Попробуйте другое."

    if isinstance(exc, RegistrationEmailNotFound):
        return "Код подтверждения не найден. Отправьте код ещё раз."

    if isinstance(exc, (EmailNotFound, IDNotFound)):
        return "Данные не найдены."

    if isinstance(exc, BadRequest):
        return "Сервис не смог обработать запрос. Попробуйте позже."

    if isinstance(exc, (DBReturnedAVoid, NoPythonProcessesFound, MediaNotFound)):
        return "Внутренняя ошибка сервиса. Попробуйте позже."

    if isinstance(exc, (NotEnoughBalance, SubZeroInput)):
        return "Некорректная операция."

    if isinstance(exc, APIError):
        return "Ошибка сервиса. Попробуйте позже."

    message = str(exc).strip()
    return message if message else "Не удалось выполнить операцию. Попробуйте позже."

