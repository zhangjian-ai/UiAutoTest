import os
import time

from dataclasses import dataclass, field
from airtest.core.cv import Template
from airtest.core.helper import G
from airtest.utils.logger import get_logger
from hmdriver2._uiobject import UiObject
from hmdriver2.driver import Driver
from poco.pocofw import Poco
from airtest.core.ios import IOS
from _pytest.config import Config
from poco.proxy import UIObjectProxy
from poco.drivers.ios import iosPoco
from airtest.core.android import Android
from airtest.core.api import init_device, exists, swipe, double_click, wait, touch
from airtest.utils.snippet import parse_device_uri
from typing import Optional, Union, TYPE_CHECKING, List
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

from framework import img_dir
from framework.dispatch import Worker
from framework.remote import hm_remote


def retry(exc, timeout: int = 6, interval: int = 1.5):
    """
    重试装饰器

    Args:
        exc: 异常类型
        timeout: 超时时间（秒）
        interval: 重试间隔（秒）
    """
    def wrapper(func):
        def inner(*args, **kwargs):
            t = timeout
            i = interval
            while t >= 0:
                try:
                    return func(*args, **kwargs)
                except exc as e:
                    if t - i < 0:
                        raise e
                t -= interval
                time.sleep(interval)
        return inner
    return wrapper


@dataclass
class LocateAttr:
    """定位属性"""
    text: str = ""
    element: str = ""
    img_path: str = ""
    coordinates: List[int] = field(default_factory=list)


@dataclass
class Element:
    """跨平台元素定义"""
    android: LocateAttr = field(default_factory=LocateAttr)
    ios: LocateAttr = field(default_factory=LocateAttr)
    harmony: LocateAttr = field(default_factory=LocateAttr)
    desc: str = ""


class ElementProxy:
    """
    元素代理
    """

    def __init__(self, element: Element, logging=get_logger("airtest")):
        self.element = element
        self.logging = logging

    def __call__(self, poco) -> Optional[UIObjectProxy]:
        """
        允许通过元素实例直接调用element
        """
        obj = self._ui_object(poco)

        if not obj:
            raise RuntimeError("当前元素不支持调用")

        return obj

    def _ea(self, platform: str) -> LocateAttr:
        """获取指定平台的ElementAttr"""
        ea = getattr(self.element, platform.lower(), None)

        if not ea:
            raise RuntimeError(f"当前元素暂不支持 {platform}")

        return ea

    def _ui_object(self, poco) -> Optional[UIObjectProxy]:
        """获取UI对象"""
        ea = self._ea(poco.platform)

        if poco.platform == "harmony":
            pass
        else:
            if ea.element and "lambda" in ea.element:
                ele = eval(ea.element)(poco)
                if ele.exists():
                    return ele

            if isinstance(ea.element, str) and isinstance(ea.text, str):
                ele = poco(ea.element, text=ea.text)
                if ele.exists():
                    return ele

            if isinstance(ea.element, str):
                ele = poco(ea.element)
                if ele.exists():
                    return ele

            if isinstance(ea.text, str):
                ele = poco(text=ea.text)
                if ele.exists():
                    return ele

    def get_coordinates(self, poco):
        """
        获取屏幕坐标
        """
        ea = self._ea(poco.platform)

        if not ea.coordinates:
            return

        if poco.platform == "android":
            width, height = poco.get_screen_size()
            std_x = 720
            std_y = 1280
            coord1 = int(width / std_x * ea.coordinates[0])
            coord2 = int(height - width / std_x * (std_y - ea.coordinates[1]))
            self.logging.info(f"坐标：{coord1}, {coord2}")
            return coord1, coord2

        else:
            coord1 = int(ea.coordinates[0])
            coord2 = int(ea.coordinates[1])
            self.logging.info(f"坐标：{coord1}, {coord2}")
            return coord1, coord2

    def exists(self, poco):
        """
        检查元素是否存在

        Args:
            poco: Poco实例，用于查找元素、文本或图像

        Returns:
            bool: 如果找到元素返回True，否则返回False
        """
        obj = self._ui_object(poco)
        ea = self._ea(poco.platform)

        if obj:
            return True

        if ea.img_path and os.path.exists(os.path.join(img_dir, ea.img_path)):
            return exists(Template(os.path.join(img_dir, ea.img_path)))

        return False

    def touch(self, poco):
        """通过坐标点击元素"""
        coordinates = self.get_coordinates(poco)

        if coordinates:
            return touch(coordinates, duration=0.05)
        else:
            raise RuntimeError("控件或按键属性(坐标)不完整，请检查")

    @retry(exc=ReferenceError)
    def click(self, poco):
        """
        点击元素

        Args:
            poco: Poco实例，用于进行UI测试和设备控制

        Raises:
            ReferenceError: 如果元素未找到
        """
        ea = self._ea(poco.platform)
        if self.exists(poco):
            obj = self._ui_object(poco)
            if obj:
                return obj.click()
            else:
                touch(Template(os.path.join(img_dir, ea.img_path)))

        elif ea.coordinates:
            return touch(self.get_coordinates(poco), duration=0.05)
        else:
            raise ReferenceError(f"ElementNotFound: {self.element.desc}")

    @retry(exc=ReferenceError)
    def swipe(self, poco, direction, focus=None, duration=0.5):
        """
        滑动元素

        Args:
            poco: Poco实例
            direction: 滑动的方向
            focus: 焦点位置
            duration: 滑动持续时间（秒）
        """
        ea = self._ea(poco.platform)
        if self.exists(poco):
            obj = self._ui_object(poco)
            if obj:
                return obj.swipe(direction, focus, duration)
            else:
                swipe(Template(os.path.join(img_dir, ea.img_path)), direction)

        elif ea.coordinates:
            return swipe(self.get_coordinates(poco), direction)
        else:
            raise ReferenceError(f"ElementNotFound: {self.element.desc}")

    @retry(exc=ReferenceError)
    def long_click(self, poco, duration=2.0):
        """
        长按元素

        Args:
            poco: Poco实例
            duration: 长按持续时间（秒）
        """
        ea = self._ea(poco.platform)
        if self.exists(poco):
            obj = self._ui_object(poco)
            if obj:
                return obj.long_click(duration=duration)
            else:
                swipe(Template(os.path.join(img_dir, ea.img_path)), vector=[0.01, 0.01], duration=duration)

        elif ea.coordinates:
            return swipe(self.get_coordinates(poco), vector=[0.01, 0.01], duration=duration)
        else:
            raise ReferenceError(f"ElementNotFound: {self.element.desc}")

    @retry(exc=ReferenceError)
    def double_click(self, poco):
        """
        双击元素

        Args:
            poco: Poco实例
        """
        ea = self._ea(poco.platform)
        if self.exists(poco):
            obj = self._ui_object(poco)
            if obj:
                return obj.double_click()
            else:
                double_click(Template(os.path.join(img_dir, ea.img_path)))

        elif ea.coordinates:
            return double_click(self.get_coordinates(poco))
        else:
            raise ReferenceError(f"ElementNotFound: {self.element.desc}")

    def get_text(self, poco):
        """
        获取元素文本

        Args:
            poco: Poco实例

        Returns:
            str: 元素的文本内容
        """
        # 先检查元素是否存在
        self.wait_for_appearance(poco, timeout=6)

        obj = self._ui_object(poco)
        if obj:
            return obj.get_text() or ""
        else:
            raise ReferenceError(f"ElementNotFound: {self.element.desc}")

    def set_text(self, poco, string):
        """
        设置元素文本

        Args:
            poco: Poco实例
            string: 要设置的文本
        """
        # 先检查元素是否存在
        self.wait_for_appearance(poco, timeout=6)

        obj = self._ui_object(poco)
        if obj:
            return obj.set_text(string)
        else:
            raise ReferenceError(f"ElementNotFound: {self.element.desc}")

    @retry(exc=ReferenceError)
    def get_attr(self, poco, parm_name):
        """
        获取元素属性

        Args:
            poco: Poco实例
            parm_name: 属性名称

        Returns:
            属性值
        """
        # 先检查元素是否存在
        self.wait_for_appearance(poco, timeout=6)

        obj = self._ui_object(poco)
        if obj:
            return obj.attr(parm_name)
        else:
            raise ReferenceError(f"ElementNotFound: {self.element.desc}")

    def wait_for_appearance(self, poco, timeout=12):
        """
        等待元素出现

        Args:
            poco: Poco实例
            timeout: 等待超时时间（秒）
        """
        obj = self._ui_object(poco)
        ea = self._ea(poco.platform)
        if obj:
            return obj.wait_for_appearance(timeout)

        if ea.img_path and os.path.exists(os.path.join(img_dir, ea.img_path)):
            return wait(Template(os.path.join(img_dir, ea.img_path)), timeout=timeout)

        raise RuntimeError("当前元素不支持本方法")

    def wait_for_disappearance(self, poco, timeout=12):
        """
        等待元素消失

        Args:
            poco: Poco实例
            timeout: 等待超时时间（秒）
        """
        obj = self._ui_object(poco)
        if obj:
            return obj.wait_for_disappearance(timeout)

        raise RuntimeError("当前元素不支持本方法")


class IosProxy(iosPoco):
    """
    新增device属性，与android保持一致
    """
    def __init__(self, device=None, **kwargs):
        self.device = device
        super(IosProxy, self).__init__(device=device, **kwargs)


class HarmonyProxy(Driver):
    """
    新增device属性，与android保持一致
    """
    def __init__(self, serial: Optional[str] = None):
        super(HarmonyProxy, self).__init__(serial)
        self.device = self


class ProxyMixin:
    """
    代理扩展类
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
                poco = IosProxy(device=device, pre_action_wait_for_appearance=6)

            elif platform.lower() == "harmony":
                if params.get("host"):
                    host, port = params.get("host")
                    hm_remote(host, port)

                poco = HarmonyProxy(uuid or None)

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
    class DeviceProxy(ProxyMixin, AndroidUiautomationPoco, iosPoco, Driver):
        ...

else:
    # 运行时：只继承PocoMixin，避免初始化冲突
    class DeviceProxy(ProxyMixin):
        """
        设备代理
        tips: 不要把我当做代理，我就是你想要的Poco
        """

        def __init__(self, config: Config):
            ProxyMixin.__init__(self, config)

            # 把自己给config引用
            config.option.__dict__["poco"] = self
