#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_01.part_a import SnacksList


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        197301
        """
        return SnacksListExtended.from_calories_text(_input)\
            .get_3_largest_calories_count()


class SnacksListExtended(SnacksList):
    def get_3_largest_calories_count(self) -> int:
        """
        >>> SnacksListExtended(snacks_list=[
        ...     [1000, 2000, 3000], [4000], [5000, 6000], [7000, 8000, 9000],
        ...     [10000],
        ... ]).get_3_largest_calories_count()
        45000
        """
        return sum(sorted(map(sum, self.snacks_list), reverse=True)[:3])


Challenge.main()
challenge = Challenge()
