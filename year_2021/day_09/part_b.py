#!/usr/bin/env python3
from functools import reduce
from typing import Set, List, Union, Tuple

from aox.challenge import Debugger
from aox.styling.shortcuts import make_colour
from utils import BaseChallenge, Point2D
from year_2021.day_09 import part_a
from year_2021.day_09.part_a import Cave


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        891684
        """
        cave = CaveExtended.from_cave_text(_input)
        return cave.get_3_largest_basins_size_product()

    def play(self):
        cave = CaveExtended.from_cave_text(self.input)
        print(sorted(cave.get_basin_sizes(), reverse=True))
        print(cave.get_basins_str(coloured=True))


class CaveExtended(Cave):
    def get_basins_str(self, coloured: bool = False) -> str:
        """
        >>> print(CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_basins_str())
        21   43210
        3 878 4 21
         85678 8 2
        87678 678
         8   65678
        """
        basin_colour = make_colour(fg='green')
        low_points = self.get_low_points()
        basin_points = reduce(set.union, map(self.get_basin, low_points))
        return "\n".join(
            "".join(
                (
                    basin_colour(str(height))
                    if Point2D(x, y) in basin_points else
                    str(height)
                ) if coloured else (
                    str(height)
                    if Point2D(x, y) in basin_points else
                    " "
                )
                for x, height in enumerate(line)
            )
            for y, line in enumerate(self.heights)
        )

    def get_3_largest_basins_size_product(self) -> int:
        """
        >>> CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_3_largest_basins_size_product()
        1134
        """
        basin_sizes = sorted(self.get_basin_sizes(), reverse=True)
        largest_3_sizes = basin_sizes[:3]
        return reduce(int.__mul__, largest_3_sizes)

    def get_basin_sizes(self) -> List[int]:
        """
        >>> sorted(CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_basin_sizes())
        [3, 9, 9, 14]
        """
        return [
            len(self.get_basin(low_point))
            for low_point in self.get_low_points()
        ]

    def get_basin(self, low_point: Point2D) -> Set[Point2D]:
        """
        >>> sorted(CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_basin(Point2D(0, 0)))
        []
        >>> sorted(CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_basin(Point2D(1, 0)))
        [Point2D(x=0, y=0), Point2D(x=0, y=1), Point2D(x=1, y=0)]
        >>> len(CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_basin(Point2D(1, 0)))
        3
        >>> len(CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_basin(Point2D(9, 0)))
        9
        >>> len(CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_basin(Point2D(2, 2)))
        14
        >>> len(CaveExtended.from_cave_text('''
        ...     2199943210
        ...     3987894921
        ...     9856789892
        ...     8767896789
        ...     9899965678
        ... ''').get_basin(Point2D(6, 4)))
        9
        """
        basin = set()
        stack = [low_point]
        while stack:
            position = stack.pop(0)
            if not self.is_basin_point(position, basin=basin):
                continue
            basin.add(position)
            new_neighbours = [
                neighbour
                for neighbour in position.get_manhattan_neighbours()
                if neighbour in self
                and neighbour not in basin
                and self[neighbour] != 9
            ]
            stack.extend(new_neighbours)
        return basin

    def is_basin_point(
        self, position: Union[Tuple, Point2D], basin: Set[Point2D],
    ) -> bool:
        if not isinstance(position, Point2D):
            position = Point2D(position)

        if not basin:
            return self.is_low_point(position)

        basin_neighbours = set(position.get_manhattan_neighbours()) & basin

        height = self[position]
        min_neighbour_height = min(
            self[neighbour]
            for neighbour in basin_neighbours
            if neighbour in self
        )
        return height > min_neighbour_height


Challenge.main()
challenge = Challenge()
