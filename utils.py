import os
from pathlib import Path


def get_current_directory(file_path):
    return Path(os.path.dirname(os.path.realpath(file_path)))
