#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2020.day_03.part_a import TreeMap


def solve(_input=None):
    """
    >>> solve()
    4723283400
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return TreeMap.from_text(_input)\
        .get_product_of_tree_counts_on_slopes(
            [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)])


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
