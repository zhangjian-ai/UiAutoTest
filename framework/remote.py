import socket

from hmdriver2 import hdc
from hmdriver2.utils import FreePort
from hmdriver2._client import SOCKET_TIMEOUT, HmClient


def hm_remote(host, port):
    """
    修改hmdriver2相关源码，以支持远程设备测试
    注意：要配合transfer.py服务一起才能使用
    """

    def _build_hdc_prefix():
        if host and port:
            return f"hdc -s {host}:{port}"
        return "hdc"

    setattr(hdc, "_build_hdc_prefix", _build_hdc_prefix)

    def _connect_sock(self):
        """Create socket and connect to the uiTEST server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(SOCKET_TIMEOUT)
        self.sock.connect((host, self.local_port))

    setattr(HmClient, "_connect_sock", _connect_sock)

    def is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, port)) == 0

    setattr(FreePort, "is_port_in_use", staticmethod(is_port_in_use))
