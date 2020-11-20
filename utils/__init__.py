#!/usr/bin/env python3
import importlib
from .base_challenge import *
from .helper import *
from .point import *
from .typing_utils import *
from .collections_utils import *

test_modules = [
    importlib.import_module('utils.base_challenge'),
    importlib.import_module('utils.collections_utils'),
    importlib.import_module('utils.helper'),
    importlib.import_module('utils.point'),
    importlib.import_module('utils.typing_utils'),
]

# noinspection PyUnresolvedReferences
__all__ = [
    'test_modules',
    'test_utils',
] + sum((
    test_module.__all__
    for test_module in test_modules
), [])


def test_utils():
    import doctest
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    succeeded, failed = 0, 0
    for test_module in test_modules:
        results = doctest.testmod(
            test_module,
            optionflags=optionflags,
        )
        succeeded += results.attempted - results.failed
        failed += results.failed
    if failed:
        print(f"{failed} tests failed")
    else:
        print(f"{succeeded} tests passed")


if __name__ == "__main__":
    test_utils()
