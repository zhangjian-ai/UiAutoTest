import os

from framework.log import logger


__all__ = [
    "logger",


    "WORKDIR",
    "ALLURE",
    "ALLURE_WIN",
    "TMPDIR",
    "REPORT"
]

# 项目根目录
WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# allure 执行文件
ALLURE = os.path.join(WORKDIR, "allure", "bin", "allure")
ALLURE_WIN = os.path.join(WORKDIR, "allure", "bin", "allure.bat")

# 报告目录
TMPDIR = os.path.join(WORKDIR, "allure", "output")
REPORT = os.path.join(WORKDIR, "allure", "report")
