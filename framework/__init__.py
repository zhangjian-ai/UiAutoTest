import os

from framework.cio import read_yaml


# 项目根目录
workdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 项目配置对象
settings = read_yaml(os.path.join(workdir, "settings.yml"))["freckle"]
