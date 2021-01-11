from aox.boilerplate import DefaultBoilerplate
from aox.utils import get_current_directory

current_directory = get_current_directory()


class CustomBoilerplate(DefaultBoilerplate):
    example_part_path = current_directory.joinpath('custom_example_part.py')
