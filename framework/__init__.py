import os

from framework.loads import read_yaml


# 项目根目录
workdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 项目配置对象
settings = read_yaml(os.path.join(workdir, "settings.yml"))["freckle"]

# 元素信息yml目录
page_dir = os.path.join(workdir, "pages")

# 静态图片目录
img_dir = os.path.join(workdir, "resource", "images")
