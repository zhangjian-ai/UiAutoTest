# 封装页面公用的元素定位、操作方法
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.support.load import Driver
from utils.support.singleton import Singleton


class BasePage(metaclass=Singleton):
    def __init__(self, driver=None):
        self.driver = driver if driver else Driver.Driver
        self.chains = ActionChains(self.driver)

    def verify(self, method, value):
        """
        验证测试结果
        :param method: 验证方式。title, element, text, url
        :param value: 验证文本
        :return:
        """
        if method == "title":
            time.sleep(2)
            assert value in self.driver.title, self.driver.title
        if method == "element":
            try:
                assert isinstance(self.wait_until_presence(getattr(self, value)), WebElement)
            except AttributeError:
                assert False, f"PageObject中没有名为 {value} 的元素，请检查对应的Elements类"

    def wait_until_presence(self, location, timeout=10):
        """
        等待元素，直到被定位的元素出现，默认超时时间10s
        :param location: 被等待的元素的定位信息
        :param timeout: 超时时间
        :return: 元素对象
        """
        wait = WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.presence_of_element_located(location))
        except TimeoutException:
            assert False, f"元素 {location} 定位超时"

        return self.find_element(location)

    def get(self, url):
        """
        打开指定url网页
        :param url:
        :return:
        """
        self.driver.get(url)

    def size(self, location):
        """
        获取元素在界面上的尺寸
        :param location:
        :return: dict: {"height": 100, "width":100}
        """
        return self.find_element(location).size

    def find_element(self, location):
        """
        元素定位
        :param location: (locate type, value)
        :return: element
        """
        return self.driver.find_element(*location)

    def send_keys(self, location, key):
        """
        给定一个位置，向该位置元素输入一个值
        :param location: (locate type, value)
        :param key: str
        :return: none
        """
        self.find_element(location).send_keys(key)

    def click(self, location):
        """
        给定一个位置，点击该位置的元素
        :param location:
        :return:
        """
        self.find_element(location).click()

    def drag_and_drop_by_offset(self, source, x_offset=0, y_offset=0):
        """
        拖拽元素到某个位置后松开
        :param source: 拖动的元素对象
        :param x_offset:
        :param y_offset:
        :return: self
        """
        self.chains.drag_and_drop_by_offset(source, x_offset, y_offset).perform()
