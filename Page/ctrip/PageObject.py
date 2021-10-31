from Base import BasePage
from utils.support.singleton import Singleton
from .elements import *


class LoginPage(BasePage, LoginPageElements, metaclass=Singleton):
    """登录页面"""

    # 业务操作
    def login(self, username, password):
        """登录操作"""
        self.get(self.url)
        self.send_keys(self.loginname, username)
        self.send_keys(self.pwd, password)

        # 如果有滑块验证则拖动滑块
        drag_btn = self.wait_until_presence(self.drag_btn, 1)
        if drag_btn:
            distance = self.size(self.drag_bar).get("width")
            self.drag_and_drop_by_offset(drag_btn, distance, 0)

        self.click(self.submit)
