import os
import yaml
import inspect

from typing import get_type_hints
from airtest.utils.logger import get_logger

from framework import page_dir
from framework.proxy import Element, LocateAttr, ElementProxy


def read_yaml(file: str) -> dict:
    """
    :param file: absolute path
    :return: dict of content
    """

    with open(file, "r", encoding="utf8") as f:
        content = yaml.safe_load(f.read())

    return content


def create_element_from_yaml(element_data: dict) -> Element:
    """
    从YAML数据创建Element对象
    Returns:
        Element对象
    """
    desc = element_data.get('desc', '')

    # 提取各平台数据
    android_data = element_data.get('android', {})
    ios_data = element_data.get('ios', {})
    harmony_data = element_data.get('harmony', {})

    # 创建LocateAttr对象
    android_attr = LocateAttr(
        text=android_data.get('text', ''),
        element=android_data.get('element', ''),
        img_path=android_data.get('img_path', ''),
        coordinates=android_data.get('coordinates', [])
    ) if android_data else LocateAttr()

    ios_attr = LocateAttr(
        text=ios_data.get('text', ''),
        element=ios_data.get('element', ''),
        img_path=ios_data.get('img_path', ''),
        coordinates=ios_data.get('coordinates', [])
    ) if ios_data else LocateAttr()

    harmony_attr = LocateAttr(
        text=harmony_data.get('text', ''),
        element=harmony_data.get('element', ''),
        img_path=harmony_data.get('img_path', ''),
        coordinates=harmony_data.get('coordinates', [])
    ) if harmony_data else LocateAttr()

    return Element(
        android=android_attr,
        ios=ios_attr,
        harmony=harmony_attr,
        desc=desc
    )


def auto_assemble(cls):
    """
    自动装配装饰器
    """
    # 获取类所在文件名
    module_file = inspect.getfile(cls)
    file_name = os.path.basename(module_file)  # Ifly_HomePage.py
    yaml_name = file_name.replace('.py', '.yml')  # Ifly_HomePage.yml

    # 查找YAML文件（在page_elements根目录）
    yaml_path = os.path.join(page_dir, yaml_name)

    if not os.path.exists(yaml_path):
        # 如果根目录没有，尝试在android目录（向后兼容）
        yaml_path_android = os.path.join(page_dir, 'android', yaml_name)
        if os.path.exists(yaml_path_android):
            get_logger("airtest").warning(
                f"使用旧的YAML路径: {yaml_path_android}，建议迁移到新路径: {yaml_path}"
            )
            yaml_path = yaml_path_android
        else:
            raise FileNotFoundError(f"找不到元素定义文件: {yaml_path}")

    # 加载YAML数据
    try:
        yaml_data = read_yaml(yaml_path)
    except Exception as e:
        raise RuntimeError(f"加载YAML文件失败 {yaml_path}: {e}")

    # 获取当前类对应的页面数据
    class_name = cls.__name__  # HomePage
    if class_name not in yaml_data:
        raise KeyError(f"YAML文件 {yaml_name} 中找不到页面定义: {class_name}")

    page_data = yaml_data[class_name]

    # 获取类的类型注解
    try:
        type_hints = get_type_hints(cls)
    except Exception:
        # 如果获取类型注解失败，尝试直接从__annotations__获取
        type_hints = getattr(cls, '__annotations__', {})

    # 遍历所有ControlProxy类型的属性
    for attr_name, attr_type in type_hints.items():
        # 检查是否是ControlProxy类型
        is_control_proxy = False
        if attr_type == ElementProxy:
            is_control_proxy = True
        elif hasattr(attr_type, '__name__') and attr_type.__name__ == 'ControlProxy':
            is_control_proxy = True
        elif 'ControlProxy' in str(attr_type):
            is_control_proxy = True

        if is_control_proxy:
            # 检查YAML中是否有对应的元素定义
            if attr_name not in page_data:
                raise RuntimeError(f"YAML文件 {yaml_name} 中找不到元素定义: {class_name}.{attr_name}")

            element_data = page_data[attr_name]

            # 构造Element对象
            element = create_element_from_yaml(element_data)

            # 创建ControlProxy并绑定到类属性
            setattr(cls, attr_name, ElementProxy(element))

    return cls
