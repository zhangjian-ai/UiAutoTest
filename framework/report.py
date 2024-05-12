import os
import json
import pytest
import platform

from framework import OUTPUT


def set_env_to_report():
    """
    为报告添加环境信息
    在报告目录生成 environment.properties 文件
    """
    # 需要写入的环境信息
    allure_env = {
        'PythonVersion': platform.python_version(),
        'PytestVersion': pytest.__version__,
        'Platform': platform.platform()
    }
    allure_env_file = os.path.join(OUTPUT, 'environment.properties')
    with open(allure_env_file, 'w', encoding='utf-8') as f:
        for k, v in allure_env.items():
            f.write(k + "=" + v + "\n")


def set_executor_to_report():
    """
    在报告目录生成 executor.json
    """
    # 需要写入的环境信息
    allure_executor = {
        "name": "seeker",
        "type": "manual",
        "buildName": "APP TEST",
        "reportName": "TestReport"
    }
    allure_env_file = os.path.join(OUTPUT, 'executor.json')
    with open(allure_env_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(allure_executor, ensure_ascii=False, indent=4))


def set_categories_to_report():
    """
    在报告目录生成 categories.json
    """
    # 需要写入的环境信息
    categories = [
        {
            "name": "PASSED",
            "matchedStatuses": ["passed"]
        },
        {
            "name": "FAILED",
            "matchedStatuses": ["failed"]
        },
        {
            "name": "ERROR",
            "matchedStatuses": ["broken", "unknown"]
        },
        {
            "name": "SKIPPED",
            "matchedStatuses": ["skipped"]
        }
    ]
    allure_env_file = os.path.join(OUTPUT, 'categories.json')
    with open(allure_env_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(categories, ensure_ascii=False, indent=4))


def improve_report():
    set_env_to_report()
    set_executor_to_report()
    set_categories_to_report()
