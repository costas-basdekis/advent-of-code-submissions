#!/usr/bin/env python3
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_01 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return LocationRegisterExtended.from_text(_input)\
            .get_similarity_score_total()


class LocationRegisterExtended(part_a.LocationRegister):
    def get_similarity_score_total(self) -> int:
        """
        >>> LocationRegisterExtended.from_text('''
        ...     3   4
        ...     4   3
        ...     2   5
        ...     1   3
        ...     3   9
        ...     3   3
        ... ''').get_similarity_score_total()
        31
        """
        return sum(self.get_similarity_scores())

    def get_similarity_scores(self) -> List[int]:
        """
        >>> LocationRegisterExtended.from_text('''
        ...     3   4
        ...     4   3
        ...     2   5
        ...     1   3
        ...     3   9
        ...     3   3
        ... ''').get_similarity_scores()
        [9, 4, 0, 0, 9, 9]
        """
        return [
            value * self.second_list.count(value)
            for value in self.first_list
        ]


Challenge.main()
challenge = Challenge()
