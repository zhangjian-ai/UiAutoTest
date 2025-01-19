import os
import sys
import allure
import random
import pytest
import importlib

from _pytest.main import Session
from _pytest.python import Function
from xdist import is_xdist_master, is_xdist_worker

from framework import workdir, settings
from framework.proxy import PocoProxy
from framework.report import improve_report


def pytest_addoption(parser):
    parser.addoption("--devs", action="append", default=["Android:///", "iOS:///127.0.0.1:8190/?udid=00008101-00112CCA3AE0001E"])
    parser.addoption("--app", action="store", default="com.demo.demo")


def pytest_configure(config):
    """
    config hook
    :param config:
    :return:
    """

    # 检查日志目录
    # TODO 以下变量应该通过settings来配置使用
    tmp_dir = config.get("report.tmp_dir")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    dst_dir = config.get("report.dst_dir")
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)


def pytest_pyfunc_call(pyfuncitem: Function):
    """
    动态写入用例信息
    :param pyfuncitem:
    :return:
    """
    # 用例名称
    func = pyfuncitem.function
    allure.dynamic.title(func.__name__)
    allure.dynamic.description((func.__doc__ or func.__name__).strip())

    # 功能名称
    cls = pyfuncitem.cls
    allure.dynamic.story((cls.__doc__ or cls.__name__).strip())

    # 模块所在包
    package_name = pyfuncitem.module.__package__
    package = importlib.import_module(package_name)
    feature = (package.__doc__ or package.__name__).strip()
    allure.dynamic.feature(feature)

    # 产品包
    product_name = ".".join(package_name.split(".", 2)[:2])
    product = importlib.import_module(product_name)
    project = product.__doc__

    if project == feature:
        project = product.__name__

    allure.dynamic.epic(project)

    # 添加附件
    # allure.attach.file(os.path.join(workdir, "readme.md"), name="readme.md")


def pytest_sessionfinish(session: Session, exitstatus):
    """
    测试结束时的勾子
    """

    # 生成报告
    # --clean 表示清楚原先的数据
    if is_xdist_master(session) and hasattr(session.config.option, "alluredir"):
        improve_report()
        args = f"generate --single-file {settings['report']['tmp_dir']} -o {settings['report']['dst_dir']} --clean"
        if "windows" in sys.platform.lower():
            os.system(f"{settings['report']['win_cmd']} {args}")
        else:
            os.system(f"{settings['report']['win_cmd']} {args}")


@pytest.fixture(scope="session", autouse=True)
def poco(pytestconfig):
    """
    设备连接
    :param pytestconfig:
    :return:
    """

    poco = PocoProxy(pytestconfig)
    poco.switch(os=pytestconfig.getoption("meta.target"))

    return poco
