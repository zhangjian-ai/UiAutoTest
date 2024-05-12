本项目介绍UI自动化测试相关的技术栈。覆盖Web和客户端(ios、android、windows、Mac 等)。



## PO模式简介

> PO模型是:Page Object Model的简写 页面对象模型
>
> PO设计模式是Selenium自动化测试中最佳的设计模式之一，主要体现在对界面交互细节的封装

就是把测试页面和测试脚本进行分离，即把页面封装成类，供测试脚本进行调用。

分层机制，让不同层去做不同类型的事情，让代码结构清晰，增加复用性。

核心思想是通过对界面元素的封装减少冗余代码，同时在后期维护中，若元素定位发生变化， 只需要调整页面元素封装的代码，提高测试用例的可维护性、可读性。

PO模式可以把一个页面分为三层，对象库层、操作层、业务层。

- 对象层：每个页面封装为一个类，属性是页面上的元素。
- 操作层：封装对页面、元素的操作，形成一个或多个操作类。
- 业务层：将一个或多个操作组合起来完成一个业务功能。比如登录：需要输入帐号、密码、点击登录三个操作。



**优点：**

1. 提高代码的可读性
2. 减少了代码的重复
3. 提高代码的可维护性，特别是针对UI界面频繁的项目

**缺点：**

1. 造成项目结构比较复杂，因为是根据流程进行了模块化处理



## Selenium

> 以下所有示例，均已Chrome浏览器为例
>
> Selenium 适用于常规的web ui



### 创建驱动

通常驱动实例名取为`driver`，是测试代码得以启动浏览器、执行相关操作的纽带，一切动作均以此为媒介。

```python
from selenium import webdriver

# 创建driver之前，通常会先创建一个浏览器的配置对象，实现对浏览器的一些配置
chromeOptions = webdriver.ChromeOptions()

# 取消浏览器打开时显示的正在监控提示
chromeOptions.add_argument('disable-infobars') 

# 添加User-Agent。对于很多网站都会限制非真实的代码请求
chromeOptions.add_argument('--user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0')

 # 添加代理。模拟真实的请求来源地址
chromeOptions.add_argument("--proxy-server=http://127.0.0.1")

# 浏览器后台运行模式，不在页面上打开窗口
chromeOptions.add_argument('--headless')

# 禁用图片及js。2是禁用, 1是允许
prefs = {
    'profile.default_content_setting_values': {
         'images': 2,
         'javascript': 2,
    }
}
options.add_experimental_option('prefs', prefs)

# 隐藏window.navigator.webdriver特征参数 （有时候能反爬）
option.add_experimental_option('excludeSwitches', ['enable-automation'])

# 创建driver时指定驱动程序。也可以将驱动程序配置到系统环境变量就可无需指定
# 注意：在新版中 executable_path 已被移除，使用Service实例来替换驱动路径
driver = webdriver.Chrome(options=chromeOptions, executable_path="libs/chromedriver")
```



### 浏览器操作

有了driver实例之后，就可以对当前拉起的浏览器做一些列操作了

```python
# 浏览器最大化 (默认是小窗口)
driver.maximize_window()

# 浏览器最小化
driver.minimize_window()

# 设置浏览器尺寸
driver.set_window_size(height, width)

# 超时时间，如果设置了，超过时间会自动停止
driver.set_page_load_timeout(20)

# 访问网站
driver.get("http://www.baidu.com")

# 刷新网站
driver.refresh()

# 通过执行js，开启一个新的窗口
js='window.open("https://www.baidu.com");'
driver.execute_script(js)

# 切换浏览器中的窗口,window_handles返回当前窗口集合，这里代表切换到第二个窗口，如果不存在第二个窗口，会报错
driver.switch_to_window(driver.window_handles[1])

# 获取当前窗口标题名
driver.title

# 获得当前窗口对象
driver.current_window_handle

# 当前url
driver.current_url

# 当前页面源代码
driver.page_source

# 截图
driver.save_screenshot('D:/baidu.png')

# 前进、回退
browser.back()
browser.forward()

# 滑动操作，下面是整个页面滑动
driver.execute_script('window.scrollBy(0,500)') # 向下滚动500个像素
driver.execute_script('window.scrollBy(0,-500)') # 向上滚动500个像素
driver.execute_script('window.scrollBy(500,0)') # 向右滚动500个像素
driver.execute_script('window.scrollBy(-500,0)') # 向左滚动500个像素

# 滑动操作，有时候需要滑动的是页面中某个部分，那么就要以这部分的元素对象作为调用方执行滑动操作
driver.execute_script("arguments[0].scrollIntoView();", ele) # ele就表示一个元素对象，将其滑动到屏幕上可见的地方
driver.execute_script("arguments[0].scrollTo(0, 500);", ele) # 将元素滚动到当前页面高度500个像素的位置
driver.execute_script('arguments[0].scrollBy(-500,0)', ele) # 向左滚动500个像素

# 关闭当前窗口
driver.close()

# 关闭整个浏览器
driver.quit()
```



### 元素定位

Selenium提供了八种定位元素方式

1. id

2. name
3. class_name：class属性
4. tag_name：标签名称
5. link_text：超链接 a标签
6. partial_link_text：超链接 a标签(模糊)
7. xpath：路径(绝对路径、相对路径)
8. CSS：选择器

通常情况下，除了项目上能保证标签id的唯一性时使用ById的方式定位意外，其他都推荐使用 **相对路径的xpath** 的定位方式，结合属性值的判断，可以很好的实现元素定位，长期看来，也更稳定。

**xpath是XML路径语言，它可以用来确定xml文档中的元素位置，通过元素的路径来完成对元素的查找。HTML就是XML的一种实现方式，所以xpath是一种非常强大的定位方式。**

xpath常用定位

- 路径
  - 绝对路径：以单斜杠开头逐级开始编写，不能跳级。如: /html/body/div/p[1]/input
  - 相对路径：以双斜杠开头，双斜杠后边跟元素名称，不知元素名称可以使用*代替。如：//input
  - 当前路径：不以斜杠开头，直接从当前路径开始往后找，也不能跳级。通常在以 元素查找子元素 时使用。如：ele.find_element(By.XPATH, 'div/div[@class="playing"]/input')
- 路径试用下标：对于同层级中多个相同标签，在确认的情况下可以使用下标，减少标签的遍历。如：/html/body/div[2]/li[3]
- 路径结合属性：在Xpath中，所有的属性必须使用@符号修饰。如: //*[@id='id值']
- 路径结合逻辑(多个属性)：//*[@id='id值' and @属性='属性值']
- 路径结合层级：//*[@id='父级id属性值']/input



Xpath拓展

```python
# 定位文本值等于XXX的元素。一般适合p标签，a标签
//*[text()='XXX']

 # 定位属性包含xxx的元素【重点】。contains为关键字，不可更改。
//*[contains(@属性,'xxx')]

# 定位属性以xxx开头的元素，同样starts-with为关键字不可更改
//*[starts-with(@属性,'xxx')] 
```



### 元素操作

```python
# 以下是元素实例常用的方法

clear # 清除元素的内容
send_keys # 模拟按键输入
click # 点击元素
submit # 提交表单
size # 获取元素的尺寸,元素在界面的高度和宽度，返回一个字典。如：{'height': 56, 'width': 78}
text # 获取元素的文本
get_attribute(name) # 获取属性值。元素都是一个标签，就是获取标签里某个属性的值
location # 获取元素坐标(左上角坐标: {'x': 22, 'y': 33})，先找到要获取的元素，再调用该方法
is_displayed() # 设置该元素是否可见
is_enabled() # 判断元素是否被使用
is_selected() # 判断元素是否被选中
tag_name # 返回元素的tagName，也就是当前元素是什么标签，比如：div、p、a
context_click(elem) # 右击鼠标点击元素elem，另存为等行为
double_click(elem) # 双击鼠标点击元素elem，地图web可实现放大功能
drag_and_drop(source,target) # 拖动鼠标，源元素按下左键移动至目标元素释放
move_to_element(elem) # 鼠标移动到一个元素上
click_and_hold(elem) # 按下鼠标左键在一个元素上

send_keys(Keys.ENTER) # 按下回车键
send_keys(Keys.TAB) # 按下Tab制表键
send_keys(Keys.SPACE) # 按下空格键space
send_keys(Kyes.ESCAPE) # 按下回退键Esc
send_keys(Keys.BACK_SPACE) # 按下删除键BackSpace
send_keys(Keys.SHIFT) # 按下shift键
send_keys(Keys.CONTROL) # 按下Ctrl键
send_keys(Keys.ARROW_DOWN) # 按下鼠标光标向下按键
send_keys(Keys.CONTROL,‘a’) # 组合键全选Ctrl+A
send_keys(Keys.CONTROL,‘c’) # 组合键复制Ctrl+C
send_keys(Keys.CONTROL,‘x’) # 组合键剪切Ctrl+X
send_keys(Keys.CONTROL,‘v’) # 组合键粘贴Ctrl+V
```



**selenium提供了ActionChains类来处理鼠标、键盘事件，如鼠标移动，点击，拖拽，键盘按下抬起等。需要导入如下模块**

```python
from selenium.webdriver.common.action_chains import ActionChains
```

**ActionChains方法列表：**

```python
# 单击鼠标左键
click(on_element=None) 

# 点击鼠标左键，不松开
click_and_hold(on_element=None)

# 点击鼠标右键
context_click(on_element=None)

# 双击鼠标左键
double_click(on_element=None)

# 拖拽到某个元素然后松开
drag_and_drop(source, target)

# 拖拽到某个坐标然后松开
drag_and_drop_by_offset(source, xoffset, yoffset)

# 按下某个键盘上的键
key_down(value, element=None)

# 松开某个键
key_up(value, element=None)

# 鼠标从当前位置移动到某个坐标
move_by_offset(xoffset, yoffset) 

# 鼠标移动到某个元素
move_to_element(to_element) 

# 移动到距某个元素（左上角坐标）多少距离的位置
move_to_element_with_offset(to_element, xoffset, yoffset)

# 在某个元素位置松开鼠标左键
release(on_element=None)

# 发送某个 key 到当前焦点的元素
send_keys(val)

# 发送某个键到指定元素
send_keys_to_element(element, keys_to_send)

# 执行链中的所有动作
perform()

# 链式写法
su = find_element_by_id("su") 
ActionChains(driver).move_to_element(su).click(su).perform()

# 控制键盘示例，按下Ctrl键然后松开
ActionChains(driver).key_down(Keys.CONTROL).key_up(Keys.CONTROL).perform()
```



### 等待

- 显式等待

  ```python
  from selenium import webdriver
  from selenium.webdriver.common.by import By
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
  
  browser=webdriver.Chrome()
  url="https://www.taobao.com"
  browser.get(url)
  
  # 最长等待10s
  wait=WebDriverWait(browser,10)
  
  wait.until(EC.presence_of_element_located((By.ID,"q")))
  button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".btn-search")))
  
  browser.close()
  ```

- 隐式等待

  ```python
  # 隐式等待
  implicitly_wait 
  ```

  隐式等待，它存在整个 WebDriver 对象实例的声明周期中，隐式的等待会让一个正常响应的应用的测试变慢，它将会在寻找每个元素的时候都进行等待，这样会增加整个测试执行的时间。

  换句话说，当查找元素或元素并没有立即出现的时候，隐式等待将等待一段时间(0.5s)再查找DOM，超出设定时间后则抛出找不到元素的异常。

  ```python
  driver = webdriver.Chrome()
  url="https://www.zhihu.com/explore"
  
  driver.get(url)
  driver.implicitly_wait(10) # 在整个session中都生效
  ```

- 线程等待

  ```python
  import time
  
  # 这就是单纯的线程等待两分钟了
  time.sleep(2)
  ```

  

### JS弹窗操作

```python
# 获取弹出框文本
driver.switch_to.alert.text

# 点击确定
driver.switch_to.alert.accept()

# 点击取消
driver.switch_to.alert.dismiss()

# 设值
driver.switch_to.alert.send_keys()
```



### 下拉框操作

```python
from selenium.webdriver.support.select import Select

# 先找到下拉框元素
driver = webdriver.Chrome()
url="https://www.zhihu.com/explore"

driver.get(url)
select_element = driver.find_element(By.XPATH)

# 创建Select实例
select = Select(select_element)

# 选择 下拉框选项
select.select_by_index(index) # 以index属性值来查找匹配的元素并选择；
select.select_by_value(value) # 以value属性值来查找该option并选择；
select.select_by_visible_text(text) # 以text文本值来查找匹配的元素并选择；
select.first_selected_option() # 选择第一个option选项；
```





## Airtest&Poco

> 对于app的ui自动化，目前推荐 Airtest&Poco 两个库组合使用。相较于传统的 appium，其对元素的操作以及定位都更简单已用，且对于各端（android、ios、win、mac）都有较好的适配

此处提供官方文档以供学习：https://www.bookstack.cn/read/Airtest-1.2-zh/Home.md

项目中提供airtest&poco的使用演示
