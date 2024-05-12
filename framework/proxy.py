from poco.pocofw import Poco
from _pytest.config import Config
from poco.proxy import UIObjectProxy
from poco.drivers.ios import iosPoco
from airtest.core.api import connect_device
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class CoordinateProxy:
    """
    坐标代理
    因为坐标不能通过poco构建UIObjectProxy实例，故实现本代理类
    """

    def __init__(self, coordinate: list or tuple):
        """
        坐标通常相对于屏幕左上角
        :param coordinate: [x, y]
        """

        if len(coordinate) != 2:
            raise RuntimeError("坐标信息错误")

        self.__poco: Poco
        self.coordinate = coordinate

    def __call__(self, poco: Poco):
        """

        :param poco:
        :return:
        """

        self.__poco = poco
        return self

    def click(self):
        """
        坐标点击
        :return:
        """

        width, height = self.__poco.get_screen_size()
        self.__poco.click((self.coordinate[0] / width, self.coordinate[1] / height))


class ControlProxy:
    """
    控件代理
    """

    def __init__(self, control: dict):
        """
        :param control: 控件信息，例如：{"name": "submit", "text": "提交"}
        """
        self.control: dict = control

    def __call__(self, poco: Poco) -> UIObjectProxy:
        """
        允许用户直接调用代理对象
        :param poco:
        :return:
        """

        return poco(**self.control)


class PocoProxy:
    """
    实现对多Poco实例进行管理
    目标：支持用例并行，且实现执行步骤与 poco(device) 解耦
    """

    __slots__ = ["config", "pool"]

    def __init__(self, remotes: list, config: Config):
        """
        创建设备连接，并为之初始poco
        :param remotes: 设备连接地址列表
        :param config: pytestconfig
        """
        self.config = config

        # 根据os来创建对应的poco
        self.pool = []
        for remote in remotes:
            device = connect_device(remote)
            os = device.__class__.__name__.lower()

            if os == "android":
                poco = AndroidUiautomationPoco(device=device,
                                               screenshot_each_action=False,
                                               use_airtest_input=True,
                                               pre_action_wait_for_appearance=10)
            elif os == "ios":
                poco = iosPoco(device=device, pre_action_wait_for_appearance=10)
            else:
                raise RuntimeError("不支持的设备及操作系统")

            self.pool.append({
                "poco": poco,
                "dev_id": remote.get("id", "1949"),
                "os": os
            })

    def device_hold(self):
        """
        根据默认设备信息，占用现有设备
        用例级别占用
        注意：这里的占用是指用例执行时，在可用设备中锁定一个设备，避免其他用例在同一设备上执行
        :return:
        """

    def is_distributed(self):
        """
        判断当前测试进程是否是分布式执行
        :return:
        """

        return hasattr(self.config.option, "dist") and self.config.option.dist != "no"
