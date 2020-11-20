#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from itertools import permutations
from typing import Dict, Tuple, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, get_windows


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        207
        """
        return Network.from_distances_text(_input).get_shortest_trip_distance()


@dataclass
class Network:
    distances: Dict[Tuple[str, str], int] = field(default_factory=dict)

    re_distance = re.compile(r"^(\w+) to (\w+) = (\d+)")

    @classmethod
    def from_distances_text(cls, distances_text: str):
        """
        >>> Network.from_distances_text(
        ...     "London to Dublin = 464\\n"
        ...     "London to Belfast = 518\\n"
        ...     "Dublin to Belfast = 141\\n"
        ... )
        Network(distances={('London', 'Dublin'): 464, ('Dublin', 'London'): 464,
            ('London', 'Belfast'): 518, ('Belfast', 'London'): 518,
            ('Dublin', 'Belfast'): 141, ('Belfast', 'Dublin'): 141})
        """
        lines = distances_text.splitlines()
        distances = {}
        for lhs, rhs, distance in map(cls.extract_distance, lines):
            if (lhs, rhs) in distances:
                raise Exception(
                    f"Got duplicate distances between {lhs} and {rhs}: "
                    f"{distances[(lhs, rhs)]} and {distance}")
            distances[(lhs, rhs)] = distance
            distances[(rhs, lhs)] = distance

        return cls(distances)

    @classmethod
    def extract_distance(cls, distance_text: str) -> Tuple[str, str, int]:
        lhs, rhs, distance_str = cls.re_distance.match(distance_text).groups()
        return lhs, rhs, int(distance_str)

    def get_shortest_trip_distance(self) -> int:
        """
        >>> Network.from_distances_text(
        ...     "London to Dublin = 464\\n"
        ...     "London to Belfast = 518\\n"
        ...     "Dublin to Belfast = 141\\n"
        ... ).get_shortest_trip_distance()
        605
        """
        return self.get_trip_distance(self.get_shortest_trip())

    def get_shortest_trip(self) -> Iterable[str]:
        """
        >>> Network.from_distances_text(
        ...     "London to Dublin = 464\\n"
        ...     "London to Belfast = 518\\n"
        ...     "Dublin to Belfast = 141\\n"
        ... ).get_shortest_trip()
        ('Belfast', 'Dublin', 'London')
        """
        return min(self.get_all_trips(), key=self.get_trip_distance)

    def get_all_trips(self) -> Iterable[Iterable[str]]:
        """
        >>> # noinspection PyTypeChecker
        >>> sorted(Network.from_distances_text(
        ...     "London to Dublin = 464\\n"
        ...     "London to Belfast = 518\\n"
        ...     "Dublin to Belfast = 141\\n"
        ... ).get_all_trips())
        [('Belfast', 'Dublin', 'London'), ('Belfast', 'London', 'Dublin'),
            ('Dublin', 'Belfast', 'London'), ('Dublin', 'London', 'Belfast'),
            ('London', 'Belfast', 'Dublin'), ('London', 'Dublin', 'Belfast')]
        """
        nodes = sorted({
            node
            for edge in self.distances
            for node in edge
        })
        return permutations(nodes, len(nodes))

    def get_trip_distance(self, trip: Iterable[str]) -> int:
        """
        >>> Network().get_trip_distance([])
        0
        >>> Network.from_distances_text(
        ...     "London to Dublin = 464\\n"
        ...     "London to Belfast = 518\\n"
        ...     "Dublin to Belfast = 141\\n"
        ... ).get_trip_distance(['Dublin', 'London', 'Belfast'])
        982
        """
        return sum(
            self.distances[(lhs, rhs)]
            for lhs, rhs in get_windows(trip, 2)
        )


Challenge.main()
challenge = Challenge()
