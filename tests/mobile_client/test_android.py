from poco.exceptions import PocoTargetTimeout


def test_app_operate(poco):
    """
    使用淘宝app演示操作
    """
    # 获取设备日志，入参默认在前面加上 ' | grep'
    lines = poco.device.logcat(f"{poco.config.getoption('app')}")  # 返回一个生成器

    # 输入 '投影仪' 并点击搜索
    poco("搜索栏").click()  # 点击搜索框
    poco("com.taobao.taobao:id/searchEdit").set_text("投影仪")  # 输入内容
    poco("com.taobao.taobao:id/searchbtn").click()  # 点击搜索

    # 滑动主屏幕
    poco.swipe((0.5, 0.9), (0.5, 0.3))  # 小于1时是相对位置，参照原点在左上角。poco 直接调用只支持相对坐标操作
    poco.swipe((0.5, 0.5), (0.5, 0.9))

    # 点击 "品牌"
    poco("品牌,可选，按钮").click()

    # 滑动侧边品牌栏
    # 侧边栏尺寸 边栏宽=屏宽*0.15  边栏高=屏高*0.8
    # 使用device的swipe，支持绝对坐标操作
    width, height = poco.get_screen_size()
    bw = width * 0.15
    poco.device.swipe((bw / 2, height * 0.9), (bw / 2, height * 0.5), duration=2)

    # 等于一些不确定的界面元素，可以使用等待的形式来处理
    try:
        poco("极米").wait_for_appearance(timeout=3)
        poco("极米").click()
    except PocoTargetTimeout:
        pass

    # 获取设备日志，入参默认在前面加上 ' | grep'
    poco.logger.info("随便打印几条日志: \n")
    for line in lines:  # 生成器每次返回的是一个 bytes 文本
        print(line.decode())


def test_app_resource(poco):
    """
    获取资源使用情况
    """

    # 获取设备总的CPU、内存资源
    cpu = poco.device.shell("cat /proc/cpuinfo | grep 'processor' | wc -l")
    poco.logger.info(f"设备cpu核数: {cpu}")

    # mem = poco.device.shell("cat /proc/meminfo | grep 'MemTotal' | awk -F ':' '{print $2}'")
    mem = poco.device.shell("free -k | grep 'Mem' | awk '{print $2}'")
    swap = poco.device.shell("free -k | grep 'Swap' | awk '{print $2}'")
    poco.logger.info(f"设备内存: {mem.strip()}")
    poco.logger.info(f"交换区内存: {swap.strip()}")

    # 获取 pid
    activity = f"ACTIVITY {poco.config.getoption('app')}"
    pid = poco.device.shell(f"dumpsys activity top | grep '{activity}' | awk -F 'pid='" + " '{print $2}' | head -n 1")
    poco.logger.info(f"进程pid: {pid}")

    # 资源使用
    use_mem = poco.device.shell(f"dumpsys meminfo | grep {pid} | head -n 1 | awk -F ':' " + "'{print $1}'")
    poco.logger.info(f"使用内存: {use_mem}")

    # 资源使用率
    line = poco.device.shell(f"top -p {pid} | grep {pid}").strip()
    metric = [val.strip() for val in line.split() if val]

    poco.logger.info(f"cpu使用率: {metric[8]}")
    poco.logger.info(f"内存使用率: {metric[9]}")
