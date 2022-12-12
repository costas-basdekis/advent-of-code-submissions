#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2022.day_12 import part_a
from year_2022.day_12.part_a import DistanceMap


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        446
        """
        return DistanceMapReversed\
            .from_map_text(_input)\
            .fill_map()\
            .get_min_steps_required_to_any_level_1()


@dataclass
class DistanceMapReversed(DistanceMap):
    """
    >>> distance_map = DistanceMapReversed.from_map_text(
    ...     "Sabqponm\\n"
    ...     "abcryxxl\\n"
    ...     "accszExk\\n"
    ...     "acctuvwj\\n"
    ...     "abdefghi"
    ... ).fill_map()
    >>> distance_map.get_min_steps_required_to_any_level_1()
    29
    """
    targets: [Point2D] = field(default_factory=list)

    def __post_init__(self):
        self.targets = [
            item
            for y in range(len(self.distances))
            for x in range(len(self.distances[0]))
            for item in [Point2D(x, y)]
            if self.elevation_map[item] == 1
        ]

    def get_min_steps_required_to_any_level_1(self) -> int:
        steps = min((
            distance
            for item in self.targets
            for distance in [self[item]]
            if distance > -1
        ), default=-1)
        if steps == -1:
            raise Exception(f"No level 1 square is reachable")
        return steps

    def get_fill_start(self):
        return self.elevation_map.target

    def should_stop_filling(self) -> bool:
        return any(
            self[item] > -1
            for item in self.targets
        )

    def can_move_to_neighbour(
        self, current: Point2D, neighbour: Point2D,
    ) -> bool:
        neighbour_height = self.elevation_map[neighbour]
        current_height = self.elevation_map[current]

        can_move = neighbour_height >= (current_height - 1)
        return can_move


Challenge.main()
challenge = Challenge()
