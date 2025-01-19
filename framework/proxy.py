from poco.pocofw import Poco
from airtest.core.ios import IOS
from _pytest.config import Config
from poco.proxy import UIObjectProxy
from poco.drivers.ios import iosPoco
from airtest.core.android import Android
from airtest.core.api import connect_device
from airtest.utils.snippet import parse_device_uri
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

from framework.dispatch import Node


class ElementProxy:
    """
    元素代理，用于构建元素库
    可自定义扩展
    处理逻辑基于Poco
    """

    def __init__(self, name: str = None, text: str = None, coordinate: tuple or list = None):
        """
        :param name: 元素name属性值，基于Poco
        :param text: 元素text属性值，基于Poco
        :param coordinate: 元素坐标，对于不能使用控件定位的元素，通常使用坐标来实现对元素的操作
        """
        if not name and not text and not coordinate:
            raise RuntimeError("实例化参数至少提供一个: name text coordinate")

        if coordinate and not isinstance(coordinate, (tuple, list)):
            raise RuntimeError("coordinate 参数数据类型错误")

        self.name = name
        self.text = text
        self.coordinate = tuple(coordinate)

    def __call__(self, poco: Poco) -> UIObjectProxy or tuple:
        """
        允许用户直接调用元素代理
        如果是坐标，则返回
        """

        if self.name or self.text:
            return poco(name=self.name, text=self.text)

        return self.coordinate

    def click(self, poco: Poco):
        """
        单次点击操作
        """

        if self.name or self.text:
            poco(name=self.name, text=self.text).click()
            return

        width, height = poco.get_screen_size()
        poco.click((self.coordinate[0] / width, self.coordinate[1] / height))

    # TODO 扩展实现其他元素方法
    def double_click(self, poco: Poco):
        ...

    def swipe(self, poco: Poco, dest: tuple, duration=0.5):
        ...

    def exists(self, poco: Poco):
        ...

    def wait_for_appearance(self, poco: Poco, timeout=120):
        ...

    def wait_for_disappearance(self, poco: Poco, timeout=120):
        ...


class PocoMixin:
    """
    poco扩展类
    """

    class IOSPoco(iosPoco):
        def __init__(self, device=None, **kwargs):
            super(PocoMixin.IOSPoco, self).__init__(device, **kwargs)
            self.device = self.ios_device = device

    def __init__(self, config: Config):
        # 游标。表示当前设备对应poco实例在 poco-pool 中的索引
        self.cursor = 0

        # poco-pool
        self.poco_pool = []

        # node负责和manager控制节点通信，来获取某个设备的使用权
        self.node = Node(config=config)

        self.device: Android = ...
        self.ios_device: IOS = ...

    def switch(self, os: str = None, sn: str = None):
        """
        切换设备
        需要注意的时，使用本代理之前，必须先调用本方法
        :param os: 系统 android/ios/win/mac
        :param sn: 设备序列号
        """

        if not os and not sn:
            raise RuntimeError("可选参数必须提供一个: os sn")

        # 先看是否已经持有了目标设备
        for i, poco in enumerate(self.poco_pool):
            if poco["sn"] == sn or poco["os"] == os:
                self.cursor = i
                return

        # 如果当前没有设备就通过 node 获取一个
        uri = self.node.hold(os=os, sn=sn)

        # 创建poco并保存
        platform, uuid, params = parse_device_uri(uri)
        platform = platform.lower()

        if platform == "android":
            poco = AndroidUiautomationPoco(device=connect_device(uri),
                                           screenshot_each_action=False,
                                           use_airtest_input=True,
                                           pre_action_wait_for_appearance=10)
        elif os == "ios":
            poco = self.IOSPoco(device=connect_device(uri), pre_action_wait_for_appearance=10)
        else:
            raise RuntimeError("不支持的设备及操作系统")

        self.poco_pool.append({"poco": poco, "os": platform, "sn": uuid})
        self.cursor = len(self.poco_pool) - 1

    def __call__(self, name=None, **kw) -> UIObjectProxy:
        return Poco.__call__(self=self.poco_pool[self.cursor]["poco"], name=name, **kw)

    def __getattribute__(self, item):

        if item in ["poco_pool", "cursor", "switch", "node"]:
            return object.__getattribute__(self, item)

        return object.__getattribute__(self.poco_pool[self.cursor]["poco"], item)


class PocoProxy(PocoMixin, AndroidUiautomationPoco, iosPoco):
    """
    统一代理Poco
    """

    def __init__(self, config: Config):
        PocoMixin.__init__(self, config)
