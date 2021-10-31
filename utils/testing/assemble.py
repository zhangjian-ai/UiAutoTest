import re

from utils.support.load import Data


def build_test_data(request):
    """
    为单接口构建测试数据
    :param request: pytest request对象
    :return: 加工后的json文件数据  dict
    """
    case_id = request.param
    project_name = re.findall("tests/(\w+?)/", request.module.__file__)[0]

    # 读取测试数据
    return Data.Data[project_name][case_id]




