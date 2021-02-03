#!/usr/bin/env python3
import math

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3325347
        """
        weights = get_weights(_input)
        fuels = list(map(get_fuel, weights))
        return sum(fuels)


def get_weights(_input):
    """
    >>> get_weights("1\\n\\n2\\n3")
    [1, 2, 3]
    """
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


Challenge.main()
challenge = Challenge()
