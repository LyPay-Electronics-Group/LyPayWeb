from fastapi import HTTPException, Request
from LyPayAPI.utils.firewall import check


def firewall_validate_factory(route: str):
    """
    Функция, создающая экземпляр функции проверки доступа к роутеру
    :param route: роут проверки файерволла (``main``, ``stores``, ``admins``)
    """

    def firewall_filter(request: Request) -> None:
        """
        Не допускает исполнения кода роутера, если пользователь не проходит проверку файерволла
        :param request: ссылка на оригинальный реквест
        """

        user_session = request.session.get("user", None)
        if user_session is None:
            raise HTTPException(400)

        return check(user_session.get("ID", 0), route)

    return firewall_filter
