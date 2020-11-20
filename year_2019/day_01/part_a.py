#!/usr/bin/env python3
import doctest
import math

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    3325347
    """
    weights = get_weights(_input)
    fuels = list(map(get_fuel, weights))
    return sum(fuels)


def get_weights(_input=None):
    """
    >>> get_weights("1\\n\\n2\\n3")
    [1, 2, 3]
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    lines = _input.splitlines()
    non_empty_lines = list(filter(None, lines))
    weights = list(map(int, non_empty_lines))

    return weights


def get_fuel(weight):
    """
    >>> get_fuel(12)
    2
    >>> get_fuel(14)
    2
    >>> get_fuel(1969)
    654
    >>> get_fuel(100756)
    33583
    """
    return math.floor(weight / 3) - 2


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
