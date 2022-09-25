import shutil

import yaml

from files import common


def __get_config_dir__() -> str:
    return f"{common.get_app_dir()}/config.yml"


def __load__() -> dict:
    with open(__get_config_dir__(), "r") as stream:
        return yaml.safe_load(stream)


def save(config_data):
    with open(__get_config_dir__(), "w") as stream:
        yaml.safe_dump(config_data, stream)


def load() -> dict:
    try:
        return __load__()
    except FileNotFoundError:
        shutil.copy2(f"{common.get_app_dir()}/example.config.yml", __get_config_dir__())
        return __load__()
