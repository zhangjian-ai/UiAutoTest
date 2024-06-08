from _pytest.config import Config


class Manager:
    """
    设备管理节点
    """

    def __init__(self, config: Config):
        self.config = Config

        # 根据执行模式决定是否开始管理服务

    def close(self):
        pass


class Node:
    """
    工作节点
    """

    def __init__(self, config: Config):
        self.config = Config

        # 设备信息 {sn1: {"uri": uri, "os": os}, sn2: {"uri": uri, "os": os}, ...}
        self.devs = dict()

        # 根据执行模式决定是否开始管理服务

    def hold(self, os: str = None, sn: str = None) -> str:
        """
        向 manager 申请一个设备
        :param os: 系统类型
        :param sn: 序列号
        :return: 设备连接信息 uri
        """

    def release(self, os: str = None, sn: str = None):
        """
        释放设备
        :param os:
        :param sn:
        :return:
        """

    def close(self):
        pass
