#!/usr/bin/env python3
import importlib

test_modules_names = [
    'base_challenge',
    'helper',
    'point',
]

if __name__ == "__main__":
    import doctest
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    succeeded, failed = 0, 0
    for name in test_modules_names:
        results = doctest.testmod(
            importlib.import_module(name),
            optionflags=optionflags,
        )
        succeeded += results.attempted - results.failed
        failed += results.failed
    if failed:
        print(f"{failed} tests failed")
    else:
        print(f"{succeeded} tests passed")
else:
    from .base_challenge import *
    from .helper import *
    from .point import *

    test_modules = [
        importlib.import_module(f'utils.{name}')
        for name in test_modules_names
    ]
