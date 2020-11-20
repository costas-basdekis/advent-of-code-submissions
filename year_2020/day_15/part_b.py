#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2020.day_15 import part_a


def solve(_input=None):
    """
    >>> solve()
    238
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    return GameExtended.from_game_text(_input).get_nth_spoken_number(30000000)


class GameExtended(part_a.Game):
    """
    >>> GameExtended([0, 3, 6]).get_nth_spoken_number(30000000)
    175594
    >>> GameExtended([1, 3, 2]).get_nth_spoken_number(30000000)
    2578
    >>> GameExtended([2, 1, 3]).get_nth_spoken_number(30000000)
    3544142
    >>> GameExtended([1, 2, 3]).get_nth_spoken_number(30000000)
    261214
    >>> GameExtended([2, 3, 1]).get_nth_spoken_number(30000000)
    6895259
    >>> GameExtended([3, 2, 1]).get_nth_spoken_number(30000000)
    18
    >>> GameExtended([3, 1, 2]).get_nth_spoken_number(30000000)
    362
    """

    def add_number_to_list(self, number):
        pass


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
