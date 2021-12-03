#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1752
        """
        return Depths.from_depths_text(_input)\
            .get_increasing_differences_count()


@dataclass
class Depths:
    depths: List[int]

    @classmethod
    def from_depths_text(cls, depths_text: str) -> "Depths":
        """
        >>> Depths.from_depths_text(
        ...     "199\\n"
        ...     "200\\n"
        ...     "208\\n"
        ...     "210\\n"
        ...     "200\\n"
        ...     "207\\n"
        ...     "240\\n"
        ...     "269\\n"
        ...     "260\\n"
        ...     "263\\n"
        ... )
        Depths(depths=[199, 200, 208, 210, 200, 207, 240, 269, 260, 263])
        """
        return cls(depths=list(map(int, depths_text.splitlines())))

    def get_differences(self) -> List[int]:
        """
        >>> Depths(depths=[
        ...     199, 200, 208, 210, 200, 207, 240, 269, 260, 263
        ... ]).get_differences()
        [1, 8, 2, -10, 7, 33, 29, -9, 3]
        """
        return [
            current - previous
            for current, previous in zip(self.depths[1:], self.depths)
        ]

    def get_increasing_differences_count(self) -> int:
        """
        >>> Depths(depths=[
        ...     199, 200, 208, 210, 200, 207, 240, 269, 260, 263
        ... ]).get_increasing_differences_count()
        7
        """
        return sum(
            1
            for difference in self.get_differences()
            if difference > 0
        )


Challenge.main()
challenge = Challenge()
