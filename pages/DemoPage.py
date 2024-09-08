from framework.proxy import ElementProxy


class LoginPage:
    """
    登录页面
    """

    # 每个元素都以代理对象来呈现，每个元素实例化时的入参不一样，可以单独在配置文件中维护静态信息
    账号输入框 = ElementProxy()
    密码输入框 = ElementProxy()
    登录提交按钮 = ElementProxy()
