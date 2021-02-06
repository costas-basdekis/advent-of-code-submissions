#!/usr/bin/env python3
import importlib
from .base_challenge import *
from .helper import *
from .point import *

test_modules = [
    importlib.import_module('utils.base_challenge'),
    importlib.import_module('utils.helper'),
    importlib.import_module('utils.point'),
]

# noinspection PyUnresolvedReferences
__all__ = [
    'test_modules',
] + sum((
    test_module.__all__
    for test_module in test_modules
), [])


if __name__ == "__main__":
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
