#!/usr/bin/env python3
import doctest

from year_2019.day_01.part_a import get_weights, get_fuel


def solve(_input=None):
    """
    >>> solve()
    4985145
    """
    weights = get_weights(_input)
    fuels = list(map(get_fuel_recursive, weights))
    return sum(fuels)


def get_fuel_recursive(weight):
    """
    >>> get_fuel_recursive(12)
    2
    >>> get_fuel_recursive(14)
    2
    >>> get_fuel_recursive(1969)
    966
    >>> get_fuel_recursive(100756)
    50346
    """
    total = 0
    remaining = weight
    while remaining > 0:
        remaining = max(0, get_fuel(remaining))
        total += remaining
    return total


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
