#!/usr/bin/env python3
import importlib
from .base_challenge import *
from .helper import *
from .point import *

# noinspection PyProtectedMember
from .base_challenge import __all__ as base_challenge_all
# noinspection PyProtectedMember
from .helper import __all__ as helper_all
# noinspection PyProtectedMember
from .point import __all__ as point_all

__all__ = [
    'test_modules_names', 'test_modules',
] + (
    base_challenge_all
    + helper_all
    + point_all
)

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
    test_modules = [
        importlib.import_module(f'utils.{name}')
        for name in test_modules_names
    ]
