from airtest import aircv
from airtest.core.cv import Template

# 创建模板
t = Template("../../resource/images/ui_test05.png")

# 截屏图片，需要先read为图片对象
# 本质还是openCV读取图片
screen = aircv.imread("../../resource/images/ui_test04.png")

pos = t.match_in(screen)

print(pos)  # (487, 752)

