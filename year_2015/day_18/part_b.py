#!/usr/bin/env python3
from dataclasses import dataclass

from aox.challenge import Debugger
from utils import BaseChallenge, min_and_max_tuples, Point2D
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1006
        """
        return LifeExtended.from_life_text(_input)\
            .step_many(100, debugger=debugger)\
            .get_on_count()


@dataclass
class LifeExtended(part_a.Life):
    """
    >>> print(LifeExtended.from_life_text(
    ...     ".#.#.#\\n"
    ...     "...##.\\n"
    ...     "#....#\\n"
    ...     "..#...\\n"
    ...     "#.#..#\\n"
    ...     "####..\\n"
    ... ).step_many(5).show())
    ##.###
    .##..#
    .##...
    .##...
    #.#...
    ##...#
    """

    def __post_init__(self):
        self.turn_corners_on()

    def turn_corners_on(self):
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.grid)
        for x in (min_x, max_x):
            for y in (min_y, max_y):
                self.grid[Point2D(x, y)] = True

        return self


Challenge.main()
challenge = Challenge()
