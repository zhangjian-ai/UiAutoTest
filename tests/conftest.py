import pytest
import logging

from airtest.core.api import connect_device

from tests.mobile_client.utils import AndroidPoco, ApplePoco


def pytest_addoption(parser):
    parser.addoption("--uri", action="store", default="Android:///")
    parser.addoption("--app", action="store", default="com.taobao.taobao")


def pytest_configure(config):
    """
    config hook
    :param config:
    :return:
    """
    # 处理一下日志输出
    airtest = logging.getLogger("airtest")
    formatter = logging.Formatter(fmt="\n%(asctime)s | %(name)s | %(levelname)s - %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    airtest.handlers = [handler]


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

    return poco


@pytest.fixture(autouse=True)
def _(poco):
    """
    前后置
    """
    # 启动app
    poco.device.start_app(poco.config.getoption("app"))

    yield

    # 停止app
    poco.device.stop_app(poco.config.getoption("app"))
