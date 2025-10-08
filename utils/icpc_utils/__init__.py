import importlib

from .base_icpc_challenge import *
from .default_boilerplate_with_icpc import *
from .icpc_command_line import *
from .icpc_controller import *

test_modules = [
    importlib.import_module('utils.icpc_utils.base_icpc_challenge'),
    importlib.import_module('utils.icpc_utils.default_boilerplate_with_icpc'),
    importlib.import_module('utils.icpc_utils.icpc_command_line'),
    importlib.import_module('utils.icpc_utils.icpc_controller'),
]

# noinspection PyUnresolvedReferences
__all__ = [
    'test_modules',
] + sum((
    test_module.__all__
    for test_module in test_modules
), [])
