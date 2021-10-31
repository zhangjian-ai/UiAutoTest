from selenium.webdriver.common.by import By

BASE_URL = "https://passport.ctrip.com"


class LoginPageElements:
    # 页面地址
    url = BASE_URL + "/user/login"

    # 页面元素
    loginname = (By.ID, "nloginname")
    pwd = (By.ID, "npwd")
    err = (By.ID, "nerr")
    submit = (By.ID, "nsubmit")
    drag_btn = (By.CLASS_NAME, "cpt-drop-btn")
    drag_bar = (By.CLASS_NAME, "cpt-bg-bar")


