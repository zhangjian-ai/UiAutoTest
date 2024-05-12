import logging

from _pytest.config import Config
from poco.drivers.ios import iosPoco
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class PocoMixin:
    """
    poco扩展类
    """

    config: Config = None
    logger: logging.Logger = logging.getLogger("airtest")

    @classmethod
    def init_config(cls, config):
        cls.config = config


class AndroidPoco(AndroidUiautomationPoco, PocoMixin):
    """
    android poco
    """

    def __init__(self, config=None, device=None, using_proxy=True,
                 force_restart=False, use_airtest_input=False, **options):
        self.init_config(config)
        super(AndroidPoco, self).__init__(device=device,
                                          using_proxy=using_proxy,
                                          force_restart=force_restart,
                                          use_airtest_input=use_airtest_input, **options)


class ApplePoco(iosPoco, PocoMixin):
    """
    ios poco
    """

    def __init__(self, config=None, device=None, **options):
        self.init_config(config)
        super(ApplePoco, self).__init__(device=device, **options)
