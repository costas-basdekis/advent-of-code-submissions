#!/usr/bin/env python3
import utils

from year_2018.day_01.part_a import parse_shifts


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        73272
        """
        return find_repeating_frequency(parse_shifts(_input))


def find_repeating_frequency(shifts, start=0):
    """
    >>> find_repeating_frequency([1, -1])
    0
    >>> find_repeating_frequency([3, 3, 4, -2, -4])
    10
    >>> find_repeating_frequency([-6, 3, 8, 5, -6])
    5
    >>> find_repeating_frequency([7, 7, -2, -7, -4])
    14
    """
    frequency = start
    seen = {frequency}
    for shift in repeating(shifts):
        frequency += shift
        if frequency in seen:
            return frequency
        seen.add(frequency)


def repeating(items):
    while True:
        yield from items


challenge = Challenge()
challenge.main()
