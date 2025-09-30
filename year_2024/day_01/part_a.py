#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2375403
        """
        return LocationRegister.from_text(_input)\
            .get_sorted_distances_sum()


@dataclass
class LocationRegister:
    first_list: List[int]
    second_list: List[int]

    @classmethod
    def from_text(cls, text: str) -> "LocationRegister":
        """
        >>> _register = LocationRegister.from_text('''
        ...     3   4
        ...     4   3
        ...     2   5
        ...     1   3
        ...     3   9
        ...     3   3
        ... ''')
        >>> len(_register.first_list)
        6
        """
        items = [
            tuple(map(int, values))
            for line in text.strip().splitlines()
            for values in [line.strip().split("   ")]
        ]
        return cls(
            first_list=[first for first, _ in items],
            second_list=[second for _, second in items],
        )

    def get_sorted_distances_sum(self) -> int:
        """
        >>> LocationRegister.from_text('''
        ...     3   4
        ...     4   3
        ...     2   5
        ...     1   3
        ...     3   9
        ...     3   3
        ... ''').get_sorted_distances_sum()
        11
        """
        return self.sort().get_distances_sum()

    def sort(self) -> "LocationRegister":
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            first_list=sorted(self.first_list),
            second_list=sorted(self.second_list),
        )

    def get_distances_sum(self) -> int:
        """
        >>> LocationRegister.from_text('''
        ...     3   4
        ...     4   3
        ...     2   5
        ...     1   3
        ...     3   9
        ...     3   3
        ... ''').sort().get_distances_sum()
        11
        """
        return sum(self.get_distances())

    def get_distances(self) -> List[int]:
        """
        >>> LocationRegister.from_text('''
        ...     3   4
        ...     4   3
        ...     2   5
        ...     1   3
        ...     3   9
        ...     3   3
        ... ''').sort().get_distances()
        [2, 1, 0, 1, 2, 5]
        """
        return [
            abs(first - second)
            for first, second in zip(self.first_list, self.second_list)
        ]


Challenge.main()
challenge = Challenge()
