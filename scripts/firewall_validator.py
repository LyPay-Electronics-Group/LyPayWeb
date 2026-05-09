from fastapi import Request
from LyPayAPI.utils.firewall import check


def firewall_validate_factory(route: str):
    """
    Функция, создающая экземпляр функции проверки доступа к роутеру
    :param route: роут проверки файерволла (``main``, ``stores``, ``admins``, ``high``)
    """

    def firewall_filter(request: Request) -> bool:
        """
        Не допускает исполнения кода роутера, если пользователь не проходит проверку файерволла
        :param request: ссылка на оригинальный реквест
        """

        user_session = request.session.get("user", None)
        if user_session is None:
            return False

        return check(user_session.get("ID", 0), route)

    return firewall_filter
