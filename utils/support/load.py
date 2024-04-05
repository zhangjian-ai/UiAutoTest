import os

from selenium import webdriver

from utils import BASE_DIR
from utils.operation.file import load_json


class Data:
    Data = dict()

    @classmethod
    def load_local(cls):
        path = os.path.join(BASE_DIR, "Data")

        for path, _, files in os.walk(path):
            for file in files:
                # 加载json文件数据
                if file.endswith(".json"):
                    data = load_json(os.path.join(path, file))
                    cls.Data[file.split(".", 1)[0]] = data


class Driver:
    Driver = None

    def __init__(self, browser):
        if browser == "chrome":
            # 浏览器后台运行模式
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')

            driver = webdriver.Chrome(executable_path=rf"{BASE_DIR}/libs/chromedriver", options=chrome_options)
            driver.set_network_conditions()


