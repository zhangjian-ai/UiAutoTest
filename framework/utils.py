import logging


def format_logger():
    # 处理airtest日志的打印格式和等级
    airtest = logging.getLogger("airtest")
    formatter = logging.Formatter(fmt="\n%(asctime)s | %(name)s | %(levelname)s - %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    airtest.handlers = [handler]

    return airtest


logger = format_logger()
