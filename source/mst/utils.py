from LyPayAPI.mst import test1 as mst_test1
from LyPayAPI.mst import test2 as mst_test2
from LyPayAPI.mst import test3 as mst_test3


async def test1() -> bool:
    """
    Full-stack первый тест

    :return: параметр успешности теста (True/False)
    """

    hash_from_core, og_hash = await mst_test1.main()

    return hash_from_core == og_hash
