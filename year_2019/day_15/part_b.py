#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_15.part_a import get_minimum_distances, play_game


def solve(_input=None):
    """
    >>> solve()
    368
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    game = play_game(_input)
    minimum_distances = get_minimum_distances(game, game["oxygen_location"])
    return max(minimum_distances.values())


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
