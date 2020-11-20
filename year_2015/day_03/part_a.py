#!/usr/bin/env python3
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Iterable, Set, Dict

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        2081
        """
        return Path.from_path_text(_input)\
            .get_visited_positions_count()


@dataclass
class Path:
    offsets: List[Point2D]

    OFFSET_MAP = {
        ">": Point2D(1, 0),
        "<": Point2D(-1, 0),
        "^": Point2D(0, -1),
        "v": Point2D(0, 1),
    }

    @classmethod
    def from_path_text(cls, path_text: str):
        """
        >>> Path.from_path_text("")
        Path(offsets=[])
        >>> Path.from_path_text(">")
        Path(offsets=[Point2D(x=1, y=0)])
        >>> Path.from_path_text("^>v<")
        Path(offsets=[Point2D(x=0, y=-1), Point2D(x=1, y=0),
            Point2D(x=0, y=1), Point2D(x=-1, y=0)])
        >>> Path.from_path_text("^v^v^v^v^v")
        Path(offsets=[Point2D(x=0, y=-1), Point2D(x=0, y=1),
            Point2D(x=0, y=-1), Point2D(x=0, y=1),
            Point2D(x=0, y=-1), Point2D(x=0, y=1),
            Point2D(x=0, y=-1), Point2D(x=0, y=1),
            Point2D(x=0, y=-1), Point2D(x=0, y=1)])
        """
        return cls(list(map(cls.OFFSET_MAP.__getitem__, path_text.strip())))

    def get_duplicate_visited_positions_count(
            self, start: Point2D = Point2D.ZERO_POINT) -> int:
        """
        >>> Path.from_path_text(
        ...     "").get_duplicate_visited_positions_count()
        0
        >>> Path.from_path_text(
        ...     ">").get_duplicate_visited_positions_count()
        0
        >>> Path.from_path_text(
        ...     "^>v<").get_duplicate_visited_positions_count()
        1
        >>> Path.from_path_text(
        ...     "^v^v^v^v^v").get_duplicate_visited_positions_count()
        2
        """
        return len(self.get_duplicate_visited_positions(start))

    def get_duplicate_visited_positions(
            self, start: Point2D = Point2D.ZERO_POINT) -> Set[Point2D]:
        """
        >>> sorted(map(tuple, Path.from_path_text(
        ...     "").get_duplicate_visited_positions()))
        []
        >>> sorted(map(tuple, Path.from_path_text(
        ...     ">").get_duplicate_visited_positions()))
        []
        >>> sorted(map(tuple, Path.from_path_text(
        ...     "^>v<").get_duplicate_visited_positions()))
        [(0, 0)]
        >>> sorted(map(tuple, Path.from_path_text(
        ...     "^v^v^v^v^v").get_duplicate_visited_positions()))
        [(0, -1), (0, 0)]
        """
        position_counts = self.get_visited_positions_counts(start)

        return {
            position
            for position, count in position_counts.items()
            if count > 1
        }

    def get_visited_positions_count(
            self, start: Point2D = Point2D.ZERO_POINT) -> int:
        """
        >>> Path.from_path_text("").get_visited_positions_count()
        1
        >>> Path.from_path_text(">").get_visited_positions_count()
        2
        >>> Path.from_path_text("^>v<").get_visited_positions_count()
        4
        >>> Path.from_path_text("^v^v^v^v^v").get_visited_positions_count()
        2
        """
        return len(self.get_visited_positions_counts(start))

    def get_visited_positions_counts(
            self, start: Point2D = Point2D.ZERO_POINT) -> Dict[Point2D, int]:
        """
        >>> Path.from_path_text("").get_visited_positions_counts()
        {Point2D(x=0, y=0): 1}
        >>> Path.from_path_text(">").get_visited_positions_counts()
        {Point2D(x=0, y=0): 1, Point2D(x=1, y=0): 1}
        >>> Path.from_path_text("^>v<").get_visited_positions_counts()
        {Point2D(x=0, y=0): 2, Point2D(x=0, y=-1): 1, Point2D(x=1, y=-1): 1,
            Point2D(x=1, y=0): 1}
        >>> Path.from_path_text("^v^v^v^v^v").get_visited_positions_counts()
        {Point2D(x=0, y=0): 6, Point2D(x=0, y=-1): 5}
        """
        position_count = defaultdict(lambda: 0)
        for position in self.get_visited_positions(start):
            position_count[position] += 1

        return dict(position_count)

    def get_visited_positions(self, start: Point2D = Point2D.ZERO_POINT,
                              ) -> Iterable[Point2D]:
        """
        >>> list(map(tuple, Path.from_path_text("").get_visited_positions()))
        [(0, 0)]
        >>> list(map(tuple, Path.from_path_text(">").get_visited_positions()))
        [(0, 0), (1, 0)]
        >>> list(map(tuple, Path.from_path_text(
        ...     "^>v<").get_visited_positions()))
        [(0, 0), (0, -1), (1, -1), (1, 0), (0, 0)]
        >>> list(map(tuple, Path.from_path_text(
        ...     "^v^v^v^v^v").get_visited_positions()))
        [(0, 0),
            (0, -1), (0, 0),
            (0, -1), (0, 0),
            (0, -1), (0, 0),
            (0, -1), (0, 0),
            (0, -1), (0, 0)]
        """
        position = start
        yield position
        for offset in self.offsets:
            position = position.offset(offset)
            yield position


Challenge.main()
challenge = Challenge()
