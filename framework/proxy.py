from airtest.core.helper import G
from hmdriver2._uiobject import UiObject
from hmdriver2.driver import Driver
from poco.pocofw import Poco
from airtest.core.ios import IOS
from _pytest.config import Config
from poco.proxy import UIObjectProxy
from poco.drivers.ios import iosPoco
from airtest.core.android import Android
from airtest.core.api import connect_device, init_device
from airtest.utils.snippet import parse_device_uri
from typing import Optional, Union, TYPE_CHECKING
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

from framework.dispatch import Worker
from framework.ext import remote_ext


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


class IosPocoProxy(iosPoco):
    def __init__(self, device=None, **kwargs):
        self.device = device
        super(IosPocoProxy, self).__init__(device=device, **kwargs)


class HarmonyPocoProxy(Driver):

    def __init__(self, serial: Optional[str] = None):
        super(HarmonyPocoProxy, self).__init__(serial)
        self.device = self


class PocoMixin:
    """
    poco 代理扩展类
    """

    def __init__(self, config: Config):
        self.config = config

        # 测试平台类型
        self.platform = config.getoption("test.platform")

        # device manage proxy
        self.worker = Worker(config, config.getoption("test.uris").split(","))

        # 游标。表征代理类当前代理的是哪个具体的poco
        self.cursor = 0
        self.poco_pool = []

        # 没有实际意义，就图一个方便
        self.device: Union[Android, IOS, Driver] = ...

    def __call__(self, name=None, **kw) -> Union[UIObjectProxy, UiObject]:
        poco = self.poco_pool[self.cursor]
        if poco["os"] == "harmony":
            if name:
                kw["id"] = name

            return Driver.__call__(self=poco["poco"], **kw)
        else:
            return Poco.__call__(self=poco["poco"], name=name, **kw)

    def __getattribute__(self, item):
        if item in ["cursor", "poco_pool", "_build_poco", "worker", "switch_to", "release", "config",
                    "device_info", "platform"]:
            return object.__getattribute__(self, item)

        try:
            return object.__getattribute__(self.poco_pool[self.cursor]["poco"], item)
        except AttributeError:
            raise RuntimeError(f"{self.poco_pool[self.cursor]['poco'].__class__} 没有属性: {item}")

    def _build_poco(self, uri):
        """
        创建设备连接及poco实例
        :param uri: 设备连接信息
        """
        try:
            # 解析连接信息并创建链接
            platform, uuid, params = parse_device_uri(uri)

            if platform.lower() == "android":
                device = init_device(platform, uuid, **params)
                poco = AndroidUiautomationPoco(device=device, screenshot_each_action=False,
                                               use_airtest_input=True, pre_action_wait_for_appearance=6)
            elif platform.lower() == "ios":
                device = init_device(platform, uuid, **params)
                poco = IosPocoProxy(device=device, pre_action_wait_for_appearance=6)

            elif platform.lower() == "harmony":
                if params.get("host"):
                    host, port = params.get("host")
                    remote_ext(host, port)

                poco = HarmonyPocoProxy(uuid or None)

            else:
                raise RuntimeError(f"暂不支持的设备类型: {platform}")

        except Exception as e:
            raise RuntimeError(str(e))
        else:
            self.poco_pool.append({"os": platform.lower(), "sn": uuid, "poco": poco})

    def switch_to(self, os: str = None, sn: str = None):
        """
        切换设备
        """

        if not os and not sn:
            raise RuntimeError("您总得给一个参数不是~")

        # 优先处理sn
        if sn:
            sn_list = [p["sn"] for p in self.poco_pool]
            if sn in sn_list:
                self.cursor = sn_list.index(sn)
                G.DEVICE = self.poco_pool[self.cursor]["poco"].device
                return
            uri = self.worker.hold(sn=sn)
        else:
            for idx, poco in enumerate(self.poco_pool):
                if poco["os"] == os:
                    self.cursor = idx
                    G.DEVICE = self.poco_pool[self.cursor]["poco"].device
                    return
            uri = self.worker.hold(os=os)

        self._build_poco(uri)
        self.cursor = len(self.poco_pool) - 1
        G.DEVICE = self.poco_pool[self.cursor]["poco"].device

    def release(self, mode: str = ""):
        """
        释放设备连接
        :param mode: finish 时，释放所有设备。其他值 时，保留 cursor = 0 处的设备
        """

        retain = -1

        if mode == "finish":
            retain = 0
        elif self.worker.dist:
            retain = 1

        if retain != -1:
            while len(self.poco_pool) > retain:
                poco = self.poco_pool.pop()

                # 鸿蒙设备释放时删除端口转发
                if poco["os"] == "harmony":
                    poco["poco"].device._client.release()

                # 设备断连
                if hasattr(poco["poco"].device, "disconnect"):
                    getattr(poco["poco"].device, "disconnect")()

                # 设备释放
                self.worker.release(sn=poco["sn"])
                del poco

            # 如果测试结束同步关闭worker网络连接
            if retain == 0:
                self.worker.close()

        # 不管怎样都回到0索引处
        self.cursor = 0

    @property
    def device_info(self):
        """
        获取设备信息，如果有
        """
        current = self.poco_pool[self.cursor]

        if "info" not in current:
            if current["os"] == "android":
                brand = current["poco"].device.shell("getprop ro.product.brand").strip()
                model = current["poco"].device.shell("getprop ro.product.model").strip()
                sn = current["poco"].device.shell("getprop ro.serialno").strip()

                current["info"] = f"{brand} {model}[{sn}]"
            elif current["os"] == "harmony":
                brand = current["poco"].device.hdc.brand()
                model = current["poco"].device.hdc.model()
                sn = current["poco"].device.hdc.serial

                current["info"] = f"{brand} {model}[{sn}]"
            else:
                info = current["poco"].device.device_info

                current["info"] = f"{info['model']}[{info['uuid']}]"

        return current


if TYPE_CHECKING:
    # 编码时：通过多继承使得IDE可以提示
    class PocoProxy(PocoMixin, AndroidUiautomationPoco, iosPoco, Driver):
        ...

else:
    # 运行时：只继承PocoMixin，避免初始化冲突
    class PocoProxy(PocoMixin):
        """
        poco 代理类
        tips: 不要把我当做代理，我就是你想要的Poco
        """

        def __init__(self, config: Config):
            PocoMixin.__init__(self, config)

            # 把自己给config引用
            config.option.__dict__["poco"] = self
