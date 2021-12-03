#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Union, Tuple, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        566
        """
        return Cave.from_cave_text(_input).get_risk_level()


@dataclass
class Cave:
    heights: List[List[int]]

    @classmethod
    def from_cave_text(cls, cave_text: str) -> "Cave":
        """
        >>> Cave.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''')
        Cave(heights=[[2, 1, 9, 9, 9, 4, 3, 2, 1, 0],
            [3, 9, 8, 7, 8, 9, 4, 9, 2, 1], ...])
        """
        return cls(
            heights=[
                [
                    int(height_str)
                    for x, height_str in enumerate(line.strip())
                ]
                for y, line in enumerate(cave_text.strip().splitlines())
            ],
        )

    def __getitem__(self, item: Union[Tuple, Point2D]) -> int:
        """
        >>> Cave.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''')[Point2D(2, 3)]
        6
        >>> Cave.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''')[(2, 3)]
        6
        """
        if not isinstance(item, (tuple, Point2D)):
            raise Exception(
                f"Expected a tuple or Point2D, but got {type(item).__name__} "
                f"({item})"
            )
        if item not in self:
            raise KeyError(item)

        x, y = item
        return self.heights[y][x]

    def __contains__(self, item):
        if not isinstance(item, (tuple, Point2D)):
            raise Exception(
                f"Expected a tuple or Point2D, but got {type(item).__name__} "
                f"({item})"
            )
        x, y = item
        if not (0 <= y < len(self.heights)):
            return False
        if not (0 <= x < len(self.heights[y])):
            return False

        return True

    def positions(self) -> Iterable[Point2D]:
        return (
            Point2D(x, y)
            for y in range(len(self.heights))
            for x in range(len(self.heights[y]))
        )

    def get_risk_level(self) -> int:
        """
        >>> Cave.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_risk_level()
        15
        """
        return sum(
            self.get_low_point_risk_level(position)
            for position in self.get_low_points()
        )

    def get_low_point_risk_level(self, position: Point2D) -> int:
        return self[position] + 1

    def get_low_points(self) -> List[Point2D]:
        """
        >>> list(Cave.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_low_points())
        [Point2D(x=1, y=0), Point2D(x=9, y=0), Point2D(x=2, y=2),
            Point2D(x=6, y=4)]
        """
        return [
            position
            for position in self.positions()
            if self.is_low_point(position)
        ]

    def is_low_point(self, position: Union[Tuple, Point2D]) -> bool:
        """
        >>> Cave.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').is_low_point((0, 0))
        False
        >>> Cave.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').is_low_point((1, 0))
        True
        """
        if not isinstance(position, Point2D):
            position = Point2D(position)

        height = self[position]
        try:
            min_neighbour_height = min(
                self[neighbour]
                for neighbour in position.get_manhattan_neighbours()
                if neighbour in self
            )
        except Exception as base:
            raise Exception(
                f"Error while checking neighbours "
                f"{list(position.get_manhattan_neighbours())}"
            ) from base
        return height < min_neighbour_height


Challenge.main()
challenge = Challenge()
