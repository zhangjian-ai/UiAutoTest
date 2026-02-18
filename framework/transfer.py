"""
在设备挂载的宿主机上运行该脚本实现鸿蒙设备端口转发
"""

import re
import time
import socket
import logging
import threading
import subprocess

from typing import Dict, Set

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class _PortForwarder:
    """单个端口的 socket 转发器"""

    def __init__(self, port: int):
        self.port = port
        self.running = False
        self.server_socket = None
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置TCP层端口服用，在程序重启时，端口不会立即释放，为了能保证重启是继续使用端口
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1.0)

        self.thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.thread.start()
        logger.info(f"[PortForward] 启动转发 0.0.0.0:{self.port} -> 127.0.0.1:{self.port}")

    def stop(self):
        if not self.running:
            return
        logger.info(f"[PortForward] 停止转发 :{self.port}")
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except OSError:
                pass
        if self.thread:
            self.thread.join(timeout=3)

    def _accept_loop(self):
        while self.running:
            try:
                client, _ = self.server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self._bridge, args=(client,), daemon=True).start()

    def _bridge(self, client: socket.socket):
        """双向桥接 client <-> 127.0.0.1:port"""
        target = None
        try:
            target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target.connect(('127.0.0.1', self.port))

            def _pipe(src, dst):
                try:
                    while self.running:
                        data = src.recv(8192)
                        if not data:
                            break
                        dst.sendall(data)
                except OSError:
                    pass
                finally:
                    src.close()
                    dst.close()

            threading.Thread(target=_pipe, args=(client, target), daemon=True).start()
            threading.Thread(target=_pipe, args=(target, client), daemon=True).start()
        except OSError:
            client.close()
            if target:
                target.close()


class HdcPortForwardDaemon:
    """
    hdc 端口转发守护进程，将网络端口转发至本地端口
    """

    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self._forwarders: Dict[int, _PortForwarder] = {}
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    @staticmethod
    def _query_fport_ports() -> Set[int]:
        """执行 hdc fport ls，解析出所有本地转发端口"""
        try:
            result = subprocess.run(
                ["hdc", "fport", "ls"],
                capture_output=True, text=True, timeout=10
            )
            ports = set()
            for line in result.stdout.strip().splitlines():
                # 匹配第一个 tcp:端口号
                m = re.search(r'tcp:(\d+)', line)
                if m:
                    ports.add(int(m.group(1)))
            return ports
        except Exception as e:
            logger.error(f"[HdcPortForwardDaemon] 执行 hdc fport ls 失败: {e}")
            return set()

    def _sync(self):
        """同步一次：对比当前转发列表，创建/销毁 socket"""
        active_ports = self._query_fport_ports()

        with self._lock:
            current_ports = set(self._forwarders.keys())

            # 新增的端口
            for port in active_ports - current_ports:
                try:
                    fw = _PortForwarder(port)
                    fw.start()
                    self._forwarders[port] = fw
                except Exception as e:
                    logger.error(f"[HdcPortForwardDaemon] 端口 {port} 转发启动失败: {e}")

            # 消失的端口
            for port in current_ports - active_ports:
                fw = self._forwarders.pop(port)
                fw.stop()

    def start(self):
        """启动守护进程"""
        if self._running:
            return
        self._running = True

        def _loop():
            logger.info(f"[HdcPortForwardDaemon] 守护进程启动，轮询间隔 {self.interval}s")
            while self._running:
                self._sync()
                time.sleep(self.interval)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止守护进程并销毁所有转发"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.interval + 2)

        with self._lock:
            for fw in self._forwarders.values():
                fw.stop()
            self._forwarders.clear()

        logger.info("[HdcPortForwardDaemon] 守护进程已停止")

    @property
    def ports(self) -> Set[int]:
        """当前正在转发的端口集合"""
        with self._lock:
            return set(self._forwarders.keys())


if __name__ == "__main__":
    daemon = HdcPortForwardDaemon()
    daemon.start()

    logger.info("守护进程已启动，自动监听 hdc fport 端口变化，按 Ctrl+C 停止...")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        daemon.stop()
