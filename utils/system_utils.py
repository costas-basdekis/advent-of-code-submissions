import os
import sys

from typing import Callable, List, NoReturn, Optional


__all__ = ["restart_process"]


def restart_process(edit_args: Optional[Callable[[List[str]], List[str]]] = None) -> NoReturn:
    args = sys.argv
    if edit_args:
        args = edit_args(args)
    return os.execl(sys.executable, sys.executable, *args)
