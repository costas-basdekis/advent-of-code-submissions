#!/usr/bin/env python3
from itertools import starmap
from typing import Set, Dict, Iterable, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2021.day_05 import part_a
from year_2021.day_05.part_a import Line, LineSet, LineT


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        20898
        """
        return len(
            LineSetExtended.from_line_set_text(_input)
            .overlapping_points
        )


class LineSetExtended(LineSet["LineExtended"]):
    def __str__(
        self, start: Optional[Point2D] = None,
        end: Optional[Point2D] = None,
        lines: Optional[Iterable[LineT]] = None,
    ) -> str:
        """
        >>> print(LineSetExtended.from_line_set_text('''
        ...     0,9 -> 5,9
        ...     8,0 -> 0,8
        ...     9,4 -> 3,4
        ...     2,2 -> 2,1
        ...     7,0 -> 7,4
        ...     6,4 -> 2,0
        ...     0,9 -> 2,9
        ...     3,4 -> 1,4
        ...     0,0 -> 8,8
        ...     5,5 -> 8,2
        ... '''))
        1.1....11.
        .111...2..
        ..2.1.111.
        ...1.2.2..
        .112313211
        ...1.2....
        ..1...1...
        .1.....1..
        1.......1.
        222111....
        >>> print(LineSetExtended.from_line_set_text('''
        ...     0,9 -> 5,9
        ...     8,0 -> 0,8
        ...     9,4 -> 3,4
        ...     2,2 -> 2,1
        ...     7,0 -> 7,4
        ...     6,4 -> 2,0
        ...     0,9 -> 2,9
        ...     3,4 -> 1,4
        ...     0,0 -> 8,8
        ...     5,5 -> 8,2
        ... ''').__str__(lines=[LineExtended.from_line_text("6,4 -> 2,0")]))
        1....
        .1...
        ..1..
        ...1.
        ....1
        """
        if lines is None:
            lines = self.lines
        point_counts = self.get_point_counts(lines)
        if start is None:
            start = Point2D(
                min(point_counts, key=lambda point: point.x).x,
                min(point_counts, key=lambda point: point.y).y,
            )
        if end is None:
            end = Point2D(
                max(point_counts, key=lambda point: point.x).x,
                max(point_counts, key=lambda point: point.y).y,
            )
        return "\n".join(
            "".join(
                str(point_counts.get(Point2D(x, y), "."))
                for x in range(start.x, end.x + 1)
            )
            for y in range(start.y, end.y + 1)
        )

    @property
    def point_counts(self) -> Dict[Point2D, int]:
        return self.get_point_counts(self.lines)

    def get_point_counts(self, lines: Iterable[Line]) -> Dict[Point2D, int]:
        point_counts = {}
        for line in lines:
            for point in line.points:
                point_counts.setdefault(point, 0)
                point_counts[point] += 1

        return point_counts

    @property
    def overlapping_points(self) -> Set[Point2D]:
        """
        >>> len(LineSetExtended.from_line_set_text('''
        ...     0,9 -> 5,9
        ...     8,0 -> 0,8
        ...     9,4 -> 3,4
        ...     2,2 -> 2,1
        ...     7,0 -> 7,4
        ...     6,4 -> 2,0
        ...     0,9 -> 2,9
        ...     3,4 -> 1,4
        ...     0,0 -> 8,8
        ...     5,5 -> 8,2
        ... ''').overlapping_points)
        12
        """
        return self.get_overlapping_points(self.lines)


class LineExtended(Line):
    @property
    def points(self) -> Set[Point2D]:
        """
        >>> sorted(map(tuple, LineExtended.from_line_text("6,4 -> 2,0").points))
        [(2, 0), (3, 1), (4, 2), (5, 3), (6, 4)]
        """
        if self.is_diagonal:
            if abs(self.width) != abs(self.height):
                raise NotImplementedError(
                    f"Cannot produce non-45-angled diagonal points for {self} "
                    f"(width: {self.width}, height: {self.height})"
                )
            start_x, end_x = self.start.x, self.end.x
            if end_x > start_x:
                step_x = 1
            else:
                step_x = -1
            end_x += step_x
            start_y, end_y = self.start.y, self.end.y
            if end_y > start_y:
                step_y = 1
            else:
                step_y = -1
            end_y += step_y
            return set(starmap(Point2D, zip(
                range(start_x, end_x, step_x),
                range(start_y, end_y, step_y)
            )))
        else:
            return super().points


Challenge.main()
challenge = Challenge()
