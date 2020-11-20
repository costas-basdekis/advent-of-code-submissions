#!/usr/bin/env python3
from typing import Iterable

from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        804
        """
        return NetworkExtended.from_distances_text(_input)\
            .get_longest_trip_distance()


class NetworkExtended(part_a.Network):
    def get_longest_trip_distance(self) -> int:
        """
        >>> NetworkExtended.from_distances_text(
        ...     "London to Dublin = 464\\n"
        ...     "London to Belfast = 518\\n"
        ...     "Dublin to Belfast = 141\\n"
        ... ).get_longest_trip_distance()
        982
        """
        return self.get_trip_distance(self.get_longest_trip())

    def get_longest_trip(self) -> Iterable[str]:
        """
        >>> NetworkExtended.from_distances_text(
        ...     "London to Dublin = 464\\n"
        ...     "London to Belfast = 518\\n"
        ...     "Dublin to Belfast = 141\\n"
        ... ).get_longest_trip()
        ('Belfast', 'London', 'Dublin')
        """
        return max(self.get_all_trips(), key=self.get_trip_distance)


Challenge.main()
challenge = Challenge()
