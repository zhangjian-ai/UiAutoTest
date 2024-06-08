import yaml


def read_yaml(file: str) -> dict:
    """
    :param file: absolute path
    :return: dict of content
    """

    with open(file, "r", encoding="utf8") as f:
        content = yaml.safe_load(f.read())

    return content
