import importlib

from .general import *
from .primes import *

test_modules = [
    importlib.import_module('utils.math_utils.general'),
    importlib.import_module('utils.math_utils.primes'),
]

# noinspection PyUnresolvedReferences
__all__ = [
    'test_modules',
] + sum((
    test_module.__all__
    for test_module in test_modules
), [])
