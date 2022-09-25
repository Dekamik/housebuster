import os
import sys


def get_app_dir() -> str:
    if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
        return os.path.dirname((os.path.abspath(sys.executable)))
    return os.getcwd()
