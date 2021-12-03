#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_07 import part_a
from year_2021.day_07.part_a import CrabSet


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        91638945
        """
        return CrabSetExtended.from_crabs_text(_input).get_min_fuel_to_align()


class CrabSetExtended(CrabSet):
    def get_crab_distance(self, crab: int, position: int) -> int:
        """
        >>> [
        ...     CrabSetExtended([]).get_crab_distance(0, x)
        ...     for x in [1, 2, 3, 4, 5, 6, 11]
        ... ]
        [1, 3, 6, 10, 15, 21, 66]
        >>> CrabSetExtended(
        ...     [16, 1, 2, 0, 4, 2, 7, 1, 2, 14],
        ... ).get_min_fuel_to_align()
        168
        """
        distance = super().get_crab_distance(crab, position)
        return distance * (1 + distance) // 2


Challenge.main()
challenge = Challenge()
