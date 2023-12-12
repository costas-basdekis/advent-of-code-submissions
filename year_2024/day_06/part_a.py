#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Direction, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return Lab.from_text(_input).get_path_point_count()


@dataclass
class Lab:
    obstacles: Set[Point2D]
    guard_position: Point2D
    guard_direction: Direction

    @classmethod
    def from_text(cls, text: str) -> "Lab":
        """
        >>> print("!" + str(Lab.from_text('''
        ...     ....#.....
        ...     .........#
        ...     ..........
        ...     ..#.......
        ...     .......#..
        ...     ..........
        ...     .#..^.....
        ...     ........#.
        ...     #.........
        ...     ......#...
        ... ''')))
        !....#.....
        .........#
        ..........
        ..#.......
        .......#..
        ..........
        .#..^.....
        ........#.
        #.........
        ......#...
        """
        lines = text.strip().splitlines()
        obstacles = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char == "#"
        }
        guard_positions_and_directions: List[Tuple[Point2D, Direction]] = [
            (Point2D(x, y), Direction.parse(char))
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char in "^v<>"
        ]
        guard_position_and_direction, = guard_positions_and_directions
        guard_position, guard_direction = guard_position_and_direction
        return cls(obstacles=obstacles, guard_position=guard_position, guard_direction=guard_direction)

    def __str__(self) -> str:
        return self.show()

    def show(self, path_points: Optional[Set[Point2D]] = None) -> str:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return "\n".join(
            "".join(
                "#"
                if point in self.obstacles else
                "X"
                if path_points is not None and point in path_points else
                str(self.guard_direction)
                if point == self.guard_position else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.obstacles)

    def is_within_boundaries(self, position: Point2D) -> bool:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return (
            min_x <= position.x <= max_x
            and min_y <= position.y <= max_y
        )

    def get_path_point_count(self) -> int:
        """
        >>> Lab.from_text('''
        ...     ....#.....
        ...     .........#
        ...     ..........
        ...     ..#.......
        ...     .......#..
        ...     ..........
        ...     .#..^.....
        ...     ........#.
        ...     #.........
        ...     ......#...
        ... ''').get_path_point_count()
        41
        """
        return len(self.get_path_points())

    def get_path_points(self) -> Set[Point2D]:
        """
        >>> _lab = Lab.from_text('''
        ...     ....#.....
        ...     .........#
        ...     ..........
        ...     ..#.......
        ...     .......#..
        ...     ..........
        ...     .#..^.....
        ...     ........#.
        ...     #.........
        ...     ......#...
        ... ''')
        >>> print("!" + _lab.show(path_points=_lab.get_path_points()))
        !....#.....
        ....XXXXX#
        ....X...X.
        ..#.X...X.
        ..XXXXX#X.
        ..X.X.X.X.
        .#XXXXXXX.
        .XXXXXXX#.
        #XXXXXXX..
        ......#X..
        """
        points = set()
        path_summary = self.get_path_summary()
        for start, end in zip(path_summary, path_summary[1:]):
            offset = end.difference(start).to_unit()
            points.add(start)
            point = start
            while point != end:
                point = point.offset(offset)
                points.add(point)
        return points

    def get_path_summary(self) -> List[Point2D]:
        """
        >>> Lab.from_text('''
        ...     ....#.....
        ...     .........#
        ...     ..........
        ...     ..#.......
        ...     .......#..
        ...     ..........
        ...     .#..^.....
        ...     ........#.
        ...     #.........
        ...     ......#...
        ... ''').get_path_summary()
        [Point2D(x=4, y=6), Point2D(x=4, y=1), Point2D(x=8, y=1), Point2D(x=8, y=6),
            Point2D(x=2, y=6), Point2D(x=2, y=4), Point2D(x=6, y=4), Point2D(x=6, y=8),
            Point2D(x=1, y=8), Point2D(x=1, y=7), Point2D(x=7, y=7), Point2D(x=7, y=9)]
        """
        path = [self.guard_position]
        position, direction = self.guard_position, self.guard_direction
        while True:
            next_position = position.offset(direction.offset)
            if next_position in self.obstacles:
                path.append(position)
                direction = direction.clockwise
            else:
                if not self.is_within_boundaries(next_position):
                    path.append(position)
                    break
                position = next_position
        return path



Challenge.main()
challenge = Challenge()
