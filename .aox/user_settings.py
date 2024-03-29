import os
from pathlib import Path
from typing import TYPE_CHECKING

import aox.utils
if TYPE_CHECKING:
    from aox.challenge import Debugger
from aox.boilerplate import DefaultBoilerplate

dot_aox = Path(os.path.dirname(os.path.realpath(__file__)))
repo_root = dot_aox.parent
sensitive_user_settings = aox.utils.load_module_from_path(
    dot_aox.joinpath('sensitive_user_settings.py'))


AOC_SESSION_ID = sensitive_user_settings.AOC_SESSION_ID
"""
This is the `session` cookie, when you're logged in on the AOC website. You
should copy it here verbatim.

Do not put your session ID here, so that you don't run the risk of committing
the file to Git! Put it in `sensitive_user_settings.py` in the same directory.
"""

CHALLENGES_ROOT = repo_root
"""
The directory where the challenges code is on.
"""

CHALLENGES_MODULE_NAME_ROOT = None
"""
The name of the module under which the challenges leave. If there is no parent
module (or it is the root one) you can leave it as `None`.
"""

CHALLENGES_BOILERPLATE = DefaultBoilerplate(
    example_part_path=repo_root.joinpath('custom', 'custom_example_part.py'),
)
"""
The name of the class that knows where individual challenges are on the disk,
and knows how to create them.

This can be either a class, or the full class name, or an instance
"""

SITE_DATA_PATH = dot_aox.joinpath('site_data.json')
"""
The path for the cached data from the AOC site - this helps remember how many
stars you have, and also which challenges have you completed.

This needs to be a `Path` instance.
"""

README_PATH = repo_root.joinpath('README.md')
"""
The path for your README file, so that it can update the stats.

This needs to be a `Path` instance.
"""

EXTRA_MODULE_IMPORTS = []
"""
Also import these extra modules, eg if you specify custom summaries.

It needs to be a list of strings that are valid module names.
"""


def verbose_debugger_format(debugger: 'Debugger', message: str) -> str:
    from aox.utils import add_thousands_separator

    return (
        f"Step: {add_thousands_separator(debugger.step_count)}, {message}, "
        f"time: {debugger.pretty_duration_since_start}, total steps/s: "
        f"{debugger.step_frequency}, recent steps/s: "
        f"{debugger.step_frequency_since_last_report}"
    )


DEFAULT_DEBUGGER_REPORT_FORMAT = verbose_debugger_format
"""
A method that takes a `Debugger` and a message, and adds common stats that are
useful for debugging.

It can be accessed via `debugger.default_report(...)` and
`debugger.default_report_if(...)`.
"""
