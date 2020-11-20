#!/usr/bin/env python3
from itertools import zip_longest
from typing import Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        2341
        """
        return MultiPath.from_path_text(_input).get_visited_positions_count()


class MultiPath(part_a.Path):
    """
    >>> MultiPath.from_path_text("").get_visited_positions_count()
    1
    >>> MultiPath.from_path_text(">").get_visited_positions_count()
    2
    >>> MultiPath.from_path_text("^>v<").get_visited_positions_count()
    3
    >>> MultiPath.from_path_text("^v^v^v^v^v").get_visited_positions_count()
    11
    """

    def get_visited_positions(self, start: Point2D = Point2D.ZERO_POINT,
                              count: int = 2,
                              ) -> Iterable[Point2D]:
        """
        >>> list(map(tuple, MultiPath.from_path_text(
        ...     "").get_visited_positions()))
        [(0, 0), (0, 0)]
        >>> list(map(tuple, MultiPath.from_path_text(
        ...     ">").get_visited_positions()))
        [(0, 0), (0, 0), (1, 0)]
        >>> list(map(tuple, MultiPath.from_path_text(
        ...     "^>v<").get_visited_positions()))
        [(0, 0), (0, 0), (0, -1), (1, 0), (0, 0), (0, 0)]
        >>> list(map(tuple, MultiPath.from_path_text(
        ...     "^v^v^v^v^v").get_visited_positions()))
        [(0, 0), (0, 0),
            (0, -1), (0, 1),
            (0, -2), (0, 2),
            (0, -3), (0, 3),
            (0, -4), (0, 4),
            (0, -5), (0, 5)]
        """
        split_paths = [
            part_a.Path(self.offsets[index::count])
            for index in range(count)
        ]
        split_visited_positions = [
            split_path.get_visited_positions(start)
            for split_path in split_paths
        ]
        for positions in zip_longest(*split_visited_positions, fillvalue=None):
            for position in positions:
                if position is None:
                    continue
                yield position


Challenge.main()
challenge = Challenge()
