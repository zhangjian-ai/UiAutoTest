from playwright.sync_api import sync_playwright

# 启动playwright
pw = sync_playwright().start()

# 启动浏览器，返回一个Browser对象
browser = pw.chromium.launch(headless=False)

# 其他浏览器
# browser = p.firefox.launch(headless=False)
# browser = p.webkit.launch(headless=False)

# 启动用户自己安装的浏览器
# executable_path 执行可执行文件
# browser = p.chromium.launch(headless=False, executable_path='/Applications/Google Chrome.app')

# 创建一个Page对象
page = browser.new_page()
page.goto("https://www.baidu.com/")

# 打印网页标题
print(page.title())

# 输入内容进行搜索
page.locator("#kw").fill("自动化测试")
page.locator("#su").click()

# 等待页面加载，注意这里的单位 毫秒
# 另外在Playwright中不能使用time.sleep进程等待，会影响Playwright底层异步框架的逻辑
# page.wait_for_timeout(3000)

# 上面显示等待通常不推荐
# 通常建议根据目标页面某些元素是否存在来判断加载情况
page.locator(".toindex").wait_for(timeout=3000, state="visible")

# 关闭浏览器
browser.close()

# 关闭playwright
pw.stop()
