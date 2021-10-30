from Base import BasePage
from PageObject.crm.elements import *


class LoginPage(BasePage, LoginPageElements, HomePageElements):
    """登录页面"""

    # 业务操作
    def login(self, email, password, code):
        """登录操作"""
        self.get(self.url)
        self.send_keys(location=self.email, key=email)
        self.send_keys(location=self.password, key=password)
        self.send_keys(location=self.code, key=code)
        self.click(location=self.submit)
