import os
import sys

from typing import NoReturn


__all__ = ["restart_process"]


def restart_process() -> NoReturn:
    return os.execl(sys.executable, sys.executable, *sys.argv)
