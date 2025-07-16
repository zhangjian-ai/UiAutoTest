import json
import socket
import threading

from multiprocessing import Process
from airtest.utils.snippet import parse_device_uri

from framework.utils import logger


class Port:
    port = 65530


class Master(Port):
    """
    Master 作为设备调度中心
    """

    def __init__(self, uris: list):

        # 网关
        self.gw = socket.socket()
        self.gw.bind(('127.0.0.1', self.port))
        self.gw.listen(16)

        logger.info(f"Master启动，port = {self.port}")

        # 链接
        self.cons = []

        # 设备信息
        # {"sn": {"os": "android", "worker_id": None, "uri": uri}}
        devs = dict()
        for uri in uris:
            if not uri:
                continue
            platform, uuid, params = parse_device_uri(uri)
            devs[uuid] = {"os": platform, "worker_id": None, "uri": uri}

        # 监听worker
        self.process = Process(target=self.listener, args=(devs,))
        self.process.start()

    def __del__(self):
        self.close()

    @staticmethod
    def _message(data: dict = None, code: int = 0) -> bytes:
        """
        返回一个固定结构体的消息
        """
        msg = {"data": data, "code": code}

        return json.dumps(msg).encode()

    def listener(self, devs):
        """
        监听worker链接
        """
        # 线程同步锁
        lock = threading.Lock()

        while True:
            con, addr = self.gw.accept()

            self.cons.append(con)
            threading.Thread(target=self.do, args=(con, lock, devs)).start()

    @staticmethod
    def do(con, lock, devs):
        """
        接收worker的请求，并返回是否占用到设备
        多线程操作数据加锁执行
        """

        while True:
            try:
                content = con.recv(1024).decode()
            except ConnectionResetError:
                continue

            if not content:
                continue

            msg = json.loads(content)

            op = msg.get("op")  # hold release
            sn = msg.get("sn")
            os = msg.get("os")
            worker_id = msg.get("worker_id")

            # 处理worker请求
            with lock:
                if op == "hold":
                    serial_no = None
                    if sn:
                        if sn in devs and devs[sn]["worker_id"] is None:
                            serial_no = sn
                            devs[sn]["worker_id"] = worker_id
                    elif os:
                        for d_sn, dev in devs.items():
                            if dev["os"] == os and dev["worker_id"] is None:
                                serial_no = d_sn
                                dev["worker_id"] = worker_id
                                break

                    con.send(Master._message(data={serial_no: devs[serial_no]}, code=0)) \
                        if serial_no is not None else con.send(Master._message(code=-1))

                if op == "release":
                    if sn and sn in devs and devs[sn]["worker_id"] == worker_id:
                        devs[sn]["worker_id"] = None
                        con.send(Master._message(code=0))
                    else:
                        con.send(Master._message(code=-1))

    def close(self):
        """
        关闭网关
        """
        # 关闭worker连接
        if hasattr(self, "cons"):
            for con in self.cons:
                con.close()

        # 关闭服务网关
        if hasattr(self, "gw"):
            self.gw.close()

        # 终止监听进程
        if hasattr(self, "process"):
            self.process.kill()


class Worker(Port):
    """
    Worker 申请设备并管理
    """

    def __init__(self, config, uris: list = None):
        # 运行模式
        self.dist = hasattr(config, "workerinput")

        # worker_id
        self.uuid = config.workerinput["workerid"] if self.dist else None

        # 已持有的设备
        self.devs = dict()

        # 分布式和local模式区分
        if self.dist:
            # 服务连接
            self.gw = socket.socket()
            self.gw.connect(("127.0.0.1", self.port))

        else:
            if not uris:
                raise RuntimeError("无可用设备")

            for uri in uris:
                if not uri:
                    continue
                platform, uuid, params = parse_device_uri(uri)
                self.devs[uuid] = {"os": platform, "worker_id": None, "uri": uri}

    def __del__(self):
        self.close()

    def _send(self, msg):
        """
        发送消息并返回结果
        """

        if not isinstance(msg, str):
            msg = json.dumps(msg)

        msg = msg.encode()
        self.gw.send(msg)

        return json.loads(self.gw.recv(1024).decode())

    def hold(self, sn: str = None, os: str = None) -> bool:
        """
        占用设备
        """

        # 先检查当前是否有已经满足条件的设备
        if sn and sn in self.devs:
            return self.devs[sn]["uri"]

        if os:
            for dev in self.devs.values():
                if os == dev["os"]:
                    return dev["uri"]

        if self.dist:
            msg = {
                "op": "hold",
                "os": os,
                "sn": sn,
                "worker_id": self.uuid
            }

            res = self._send(msg)

            if res["code"] == 0:
                self.devs.update(res["data"])
                return tuple(res["data"].values())[0]["uri"]

        raise RuntimeError("没有满足条件的设备可使用")

    def release(self, sn: str):
        """
        释放已经占用的设备
        """
        if self.dist:
            # 从列表删除要释放的设备
            self.devs.pop(sn, None)

            # 通知master，释放设备
            msg = {
                "op": "release",
                "os": None,
                "sn": sn,
                "worker_id": self.uuid
            }
            self._send(msg)

    def close(self):
        if hasattr(self, "gw"):
            self.gw.close()
