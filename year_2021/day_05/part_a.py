#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Generic, Type, cast, List, Set

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        7674
        """
        return len(
            LineSet.from_line_set_text(_input)
            .non_diagonal_overlapping_points
        )


LineT = TV["Line"]


@dataclass
class LineSet(Generic[LineT]):
    lines: List[LineT]

    @classmethod
    def get_line_class(cls) -> Type[LineT]:
        return get_type_argument_class(cls, LineT)

    @classmethod
    def from_line_set_text(cls, line_set_text: str) -> "LineSet":
        """
        >>> LineSet.from_line_set_text('''
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
        ... ''')
        LineSet(lines=[Line(start=Point2D(x=0, y=9), end=Point2D(x=5, y=9)),
            Line(start=Point2D(x=8, y=0), end=Point2D(x=0, y=8)),
            Line(start=Point2D(x=9, y=4), end=Point2D(x=3, y=4)),
            Line(start=Point2D(x=2, y=2), end=Point2D(x=2, y=1)),
            Line(start=Point2D(x=7, y=0), end=Point2D(x=7, y=4)),
            Line(start=Point2D(x=6, y=4), end=Point2D(x=2, y=0)),
            Line(start=Point2D(x=0, y=9), end=Point2D(x=2, y=9)),
            Line(start=Point2D(x=3, y=4), end=Point2D(x=1, y=4)),
            Line(start=Point2D(x=0, y=0), end=Point2D(x=8, y=8)),
            Line(start=Point2D(x=5, y=5), end=Point2D(x=8, y=2))])
        """
        line_class = cls.get_line_class()

        return cls(
            lines=list(map(
                line_class.from_line_text,
                filter(None, line_set_text.splitlines()),
            )),
        )

    @property
    def non_diagonal_lines(self) -> List[LineT]:
        return [
            line
            for line in self.lines
            if not line.is_diagonal
        ]

    @property
    def non_diagonal_point_count(self) -> int:
        return sum(
            line.point_count
            for line in self.non_diagonal_lines
        )

    @property
    def non_diagonal_overlapping_points(self) -> Set[Point2D]:
        points = set()
        overlapping_points = set()
        for line in self.non_diagonal_lines:
            line_points = line.points
            overlapping_points |= points & line_points
            points |= line_points

        return overlapping_points


@dataclass
class Line:
    start: Point2D
    end: Point2D

    re_line = re.compile(r"^\s*(\d+),(\d+)\s*->\s*(\d+),(\d+)\s*$")

    @classmethod
    def from_line_text(cls, line_text: str) -> "Line":
        """
        >>> Line.from_line_text("0,9 -> 5,9")
        Line(start=Point2D(x=0, y=9), end=Point2D(x=5, y=9))
        >>> Line.from_line_text("541,808 -> 108,808")
        Line(start=Point2D(x=541, y=808), end=Point2D(x=108, y=808))
        """
        start_x, start_y, end_x, end_y = \
            map(int, cls.re_line.match(line_text).groups())

        return cls(start=Point2D(start_x, start_y), end=Point2D(end_x, end_y))

    @property
    def is_horizontal(self) -> bool:
        """
        >>> Line(Point2D(0, 0), Point2D(5, 0)).is_horizontal
        True
        >>> Line(Point2D(0, 0), Point2D(0, 5)).is_horizontal
        False
        >>> Line(Point2D(0, 0), Point2D(5, 5)).is_horizontal
        False
        """
        return self.start.y == self.end.y

    @property
    def is_vertical(self) -> bool:
        """
        >>> Line(Point2D(0, 0), Point2D(5, 0)).is_vertical
        False
        >>> Line(Point2D(0, 0), Point2D(0, 5)).is_vertical
        True
        >>> Line(Point2D(0, 0), Point2D(5, 5)).is_vertical
        False
        """
        return self.start.x == self.end.x

    @property
    def is_diagonal(self) -> bool:
        """
        >>> Line(Point2D(0, 0), Point2D(5, 0)).is_diagonal
        False
        >>> Line(Point2D(0, 0), Point2D(0, 5)).is_diagonal
        False
        >>> Line(Point2D(0, 0), Point2D(5, 5)).is_diagonal
        True
        """
        return not self.is_horizontal and not self.is_vertical

    @property
    def width(self) -> int:
        """
        >>> Line(Point2D(0, 0), Point2D(5, 0)).width
        6
        >>> Line(Point2D(0, 0), Point2D(0, 5)).width
        1
        >>> Line(Point2D(0, 0), Point2D(5, 5)).width
        6
        """
        return self.end.x - self.start.x + 1

    @property
    def height(self) -> int:
        """
        >>> Line(Point2D(0, 0), Point2D(5, 0)).height
        1
        >>> Line(Point2D(0, 0), Point2D(0, 5)).height
        6
        >>> Line(Point2D(0, 0), Point2D(5, 5)).height
        6
        """
        return self.end.y - self.start.y + 1

    @property
    def point_count(self) -> int:
        return max(self.width, self.height)

    @property
    def points(self) -> Set[Point2D]:
        if self.is_horizontal:
            xs = [self.start.x, self.end.x]
            min_x, max_x = min(xs), max(xs)
            return {
                Point2D(x, self.start.y)
                for x in range(min_x, max_x + 1)
            }
        elif self.is_vertical:
            ys = [self.start.y, self.end.y]
            min_y, max_y = min(ys), max(ys)
            return {
                Point2D(self.start.x, y)
                for y in range(min_y, max_y + 1)
            }
        else:
            raise NotImplementedError("Can't produce diagonal points")


Challenge.main()
challenge = Challenge()
