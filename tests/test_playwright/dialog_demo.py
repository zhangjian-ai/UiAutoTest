from playwright.sync_api import sync_playwright, Dialog

pw = sync_playwright().start()
browser = pw.chromium.launch(headless=False)
page = browser.new_page()

# 加载本地页面
page.goto("file:///Users/seeker/PycharmProjects/UiAutoTest/tests/test_playwright/dialog.html")


# 处理 弹出对话框 的 回调函数
def callback(dialog: Dialog):
    # 等待1秒
    page.wait_for_timeout(1000)
    # 输入内容并确定
    dialog.accept("赵四")

    print(dialog.message)  # 请输入您的名字：


page.on("dialog", callback)

page.press()

# 点击confirm按钮触发弹窗
page.locator("#prompt").click()
