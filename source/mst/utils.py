from LyPayAPI.mst import test1 as mst_test1
from LyPayAPI.mst import test2 as mst_test2
from LyPayAPI.mst import test3 as mst_test3


GLOBAL_TEST3_PARAMETER = 10


async def test1() -> bool:
    """
    Full-stack первый тест

    :return: параметр успешности теста (True/False)
    """

    hash_from_core, og_hash = await mst_test1.main()

    return hash_from_core == og_hash


async def test3(ID: int) -> None:
    """
    Full-stack первый тест

    :param ID: ID текущего пользователя
    :return: параметр успешности теста (True/False)
    """

    await mst_test3.main(ID)


async def test3_end(ID: int) -> bool:
    """
    Завершение третьего теста

    :param ID: ID текущего пользователя
    :return: параметр успешности теста (True/False)
    """

    return await mst_test3.end(ID)
