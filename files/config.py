import shutil

import yaml

from files import common


def __get_config_dir__() -> str:
    return f"{common.get_app_dir()}/config.yml"


def __load__(path=None) -> dict:
    with open(path or __get_config_dir__(), "r", encoding="utf8") as stream:
        return yaml.safe_load(stream)


def save(config_data: dict, path=None):
    with open(path or __get_config_dir__(), "w", encoding="utf8") as stream:
        yaml.safe_dump(config_data, stream)


def load(path=None) -> dict:
    try:
        return __load__(path)
    except FileNotFoundError:
        shutil.copy2(f"{common.get_app_dir()}/example.config.yml", __get_config_dir__())
        return __load__(path)
