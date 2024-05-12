import os
import sys
import allure
import random
import pytest
import importlib

from _pytest.main import Session
from _pytest.python import Function
from airtest.core.api import connect_device
from xdist import is_xdist_master, is_xdist_worker

from framework import TMPDIR, REPORT, ALLURE, ALLURE_WIN, WORKDIR
from framework.log import logger
from framework.mixin import AndroidPoco, ApplePoco
from framework.report import improve_report


def pytest_addoption(parser):
    parser.addoption("--uri", action="store", default="Android:///")
    parser.addoption("--app", action="store", default="com.demo.demo")


def pytest_configure(config):
    """
    config hook
    :param config:
    :return:
    """

    # 检查日志目录
    if not os.path.exists(TMPDIR):
        os.makedirs(TMPDIR)

    if not os.path.exists(REPORT):
        os.makedirs(REPORT)


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
    allure.attach.file(os.path.join(WORKDIR, "readme.md"), name="readme.md")


def pytest_sessionfinish(session, exitstatus):
    """
    测试结束时的勾子
    """

    # 生成报告
    # --clean 表示清楚原先的数据
    if is_xdist_master(session) and hasattr(session.config.option, "alluredir"):
        improve_report()
        if "windows" in sys.platform.lower():
            os.system(f"{ALLURE_WIN} generate {TMPDIR} -o {REPORT} --clean")
        else:
            os.system(f"{ALLURE} generate {TMPDIR} -o {REPORT} --clean")


@pytest.fixture(scope="session")
def device(pytestconfig):
    """
    设备连接
    :param pytestconfig:
    :return:
    """

    dev = connect_device(pytestconfig.getoption("uri"))

    return dev


@pytest.fixture(scope="session")
def poco(device, pytestconfig):
    """
    init poco
    :param device:
    :param pytestconfig:
    :return:
    """

    # 根据os来创建对应的poco
    os = device.__class__.__name__.lower()

    if os == "android":
        poco = AndroidPoco(config=pytestconfig,
                           device=device,
                           screenshot_each_action=False,
                           use_airtest_input=True,
                           pre_action_wait_for_appearance=10)
    elif os == "ios":
        poco = ApplePoco(config=pytestconfig, device=device, pre_action_wait_for_appearance=10)
    else:
        raise RuntimeError("不支持的设备及操作系统")

    # 启动app
    poco.device.start_app(poco.config.getoption("app"))

    yield poco

    # 停止app
    poco.device.stop_app(poco.config.getoption("app"))


def _(session):
    if is_xdist_master(session):
        os.environ.setdefault("honey", "12346")

    if is_xdist_worker(session):
        logger.info(os.environ.get("honey"))
        with open(f"{random.randint(1, 100)}.txt", "w") as f:
            f.write(os.environ.get("honey"))
