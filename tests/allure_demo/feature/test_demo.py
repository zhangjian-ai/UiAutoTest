import allure

from allure_commons.types import Severity

from framework import logger


class TestDemo01:
    """
    子功能一
    """

    def test_allure_01(self):
        """
        功能一中的第一个场景
        """
        logger.info("就是测着玩的桀桀桀")

        assert 1 == 1

    def test_allure_02(self):

        logger.info("就是测着玩的桀桀桀")
        assert 1 == 1


class TestDemo02:
    """
    功能二
    """

    @allure.severity(Severity.BLOCKER)
    def test_allure_01(self):
        """
        功能二中的第一个场景
        """

        assert 1 == 2

    def test_allure_02(self):
        """
        功能二中的第一个场景
        """

        assert 1 == 1
