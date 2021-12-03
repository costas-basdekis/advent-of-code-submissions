#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        336721
        """
        return CrabSet.from_crabs_text(_input).get_min_fuel_to_align()


@dataclass
class CrabSet:
    crabs: List[int]

    @classmethod
    def from_crabs_text(cls, crabs_text: str) -> "CrabSet":
        """
        >>> CrabSet.from_crabs_text("16,1,2,0,4,2,7,1,2,14")
        CrabSet(crabs=[16, 1, 2, 0, 4, 2, 7, 1, 2, 14])
        """
        return cls(crabs=list(map(int, crabs_text.split(","))))

    def get_min_fuel_to_align(self) -> int:
        """
        >>> CrabSet([16, 1, 2, 0, 4, 2, 7, 1, 2, 14]).get_min_fuel_to_align()
        37
        """
        closest_position = self.get_closest_position()
        return self.get_distance(closest_position)

    def get_closest_position(self) -> int:
        """
        >>> CrabSet([16, 1, 2, 0, 4, 2, 7, 1, 2, 14]).get_closest_position()
        2
        """
        return min(
            range(min(self.crabs), max(self.crabs) + 1),
            key=self.get_distance,
        )

    def get_distance(self, position: int) -> int:
        """
        >>> CrabSet([16, 1, 2, 0, 4, 2, 7, 1, 2, 14]).get_distance(2)
        37
        """
        return sum(
            self.get_crab_distance(crab, position)
            for crab in self.crabs
        )

    def get_crab_distance(self, crab: int, position: int) -> int:
        return abs(crab - position)


Challenge.main()
challenge = Challenge()
