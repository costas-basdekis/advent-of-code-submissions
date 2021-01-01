#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        533
        """
        return total_frequency_shift(parse_shifts(_input), 0)


def total_frequency_shift(shifts, start):
    """
    >>> total_frequency_shift([1, 2, -3], 0)
    0
    >>> total_frequency_shift([1, 2, -3], 5)
    5
    >>> total_frequency_shift([1, 2, 3], 0)
    6
    >>> total_frequency_shift([1, 2, 3], 5)
    11
    >>> total_frequency_shift([-1, -2, -3], 0)
    -6
    >>> total_frequency_shift([-1, -2, -3], 5)
    -1
    """
    return start + sum(shifts)


def parse_shifts(shifts_text):
    """
    >>> parse_shifts("+1\\n+2\\n-3\\n")
    [1, 2, -3]
    >>> parse_shifts("+1\\n+2\\n+3\\n")
    [1, 2, 3]
    >>> parse_shifts("-1\\n-2\\n-3\\n")
    [-1, -2, -3]
    """
    lines = shifts_text.splitlines()
    non_empty_lines = filter(None, lines)
    return list(map(int, non_empty_lines))


challenge = Challenge()
challenge.main()
