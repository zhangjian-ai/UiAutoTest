from _pytest.config import Config


class Manager:
    """
    设备管理节点
    """

    def __init__(self, config: Config, uris: list):
        self.config = config
        self.uris = uris

    # 监听Node节点连接
    def listener(self): ...

    # 和Node保持通信，根据Node节点的请求分发/回收设备
    def dispatch(self, os: str = None, sn: str = None): ...

    def close(self): ...


class Node:
    """
    工作节点
    """

    def __init__(self, config: Config):
        self.config = config

        # 设备信息 {sn1: {"uri": uri, "os": os}, sn2: {"uri": uri, "os": os}, ...}
        self.devs = dict()

    def hold(self, os: str = None, sn: str = None) -> str: ...

    def release(self, os: str = None, sn: str = None): ...

    def close(self): ...
