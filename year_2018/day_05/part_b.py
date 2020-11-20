#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2018.day_05 import part_a


def solve(_input=None):
    """
    >>> solve()
    5898
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _, length = part_a.Polymer(_input.strip()).find_worst_blockage()

    return length


if __name__ == '__main__':
    if doctest.testmod(part_a).failed or doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
