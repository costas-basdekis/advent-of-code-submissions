#!/usr/bin/env python3
import utils

from year_2020.day_15 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        238
        """

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


challenge = Challenge()
