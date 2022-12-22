#!/usr/bin/env python3
import re
from typing import Union, Match

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, helper
from year_2022.day_17 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> # > 1537764350475
        >>> Challenge().default_solve()
        1540804597682
        """
        return CaveExtended\
            .from_winds_text(_input)\
            .process_many_new_rocks(1000000000000, debugger=debugger)\
            .locked_top_row


class CaveExtended(part_a.Cave):
    """
    >>> cave = CaveExtended\\
    ...     .from_winds_text(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")
    >>> print(str(cave.process_many_new_rocks(1)))
    |  #### |
    +-------+
    >>> print(str(cave.process_many_new_rocks(1)))
    |   #   |
    |  ###  |
    |   #   |
    |  #### |
    +-------+
    >>> print(str(cave.process_many_new_rocks(1)))
    |  #    |
    |  #    |
    |####   |
    |  ###  |
    |   #   |
    |  #### |
    +-------+
    >>> print(str(cave.process_many_new_rocks(2)))
    |    ## |
    |    ## |
    |    #  |
    |  # #  |
    |  # #  |
    |#####  |
    |3      |
    +-------+
    >>> cave.locked_top_row
    9
    >>> cave = CaveExtended\\
    ...     .from_winds_text(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")\\
    ...     .process_many_new_rocks(2022)
    >>> cave.locked_top_row
    3068
    >>> cave = CaveExtended\\
    ...     .from_winds_text(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")\\
    ...     .process_many_new_rocks(1000000000000)
    >>> cave.locked_top_row
    1514285714288
    """

    def process_many_new_rocks(
        self, count: int, debugger: Debugger = Debugger(enabled=False),
    ) -> "CaveExtended":
        first_index_by_hash = {self.get_hash(): 0}
        locked_top_row_by_step_index = {0: self.locked_top_row}
        for step_index in debugger.stepping(range(1, count + 1)):
            self.process_new_rock()
            _hash = self.get_hash()
            if _hash in first_index_by_hash:
                period = step_index - first_index_by_hash[_hash]
                extra_iterations = (count - step_index) // period
                remaining_steps = count - step_index - extra_iterations * period
                gained_height = (
                    self.locked_top_row
                    - locked_top_row_by_step_index[first_index_by_hash[_hash]]
                )
                debugger.report(
                    f"Found duplicate after {step_index} steps, "
                    f"original was at {first_index_by_hash[_hash]}, "
                    f"period is {period}, "
                    f"extra iterations is {extra_iterations}, "
                    f"remaining steps is {remaining_steps}, "
                    f"gained height is {gained_height}"
                )
                self.elevate_points(
                    max(0, extra_iterations) * gained_height,
                )
                return self.process_many_new_rocks(
                    remaining_steps, debugger=debugger,
                )
            first_index_by_hash[_hash] = step_index
            locked_top_row_by_step_index[step_index] = self.locked_top_row
            debugger.default_report_if(
                f"Step: {step_index}/{count}, "
                f"locked top row: {self.locked_top_row}, "
                f"point count: {len(self.points)}, "
                f"hash: {_hash}"
            )
        return self

    def get_hash(self):
        min_y = min((point.y for point in self.points), default=0)
        offset = Point2D(0, -min_y)
        return (
            self.next_wind_index % len(self.winds),
            self.next_rock_index % len(part_a.Rock.DEFAULT_ROCKS),
            tuple(sorted(map(tuple, (
                point.offset(offset)
                for point in self.points
            )))),
        )

    def lock_active_rock(self) -> "CaveExtended":
        super().lock_active_rock()
        self.remove_non_top_points()
        return self

    def remove_non_top_points(self) -> "CaveExtended":
        min_y = min(
            max(ys)
            for x, ys in helper.group_by(
                self.points,
                key=lambda point: point.x,
                value=lambda point: point.y,
            ).items()
        )
        self.points = {
            point
            for point in self.points
            if point.y >= min_y
        }
        return self

    def elevate_points(self, y_offset: int) -> "CaveExtended":
        offset = Point2D(0, y_offset)
        self.points = {
            point.offset(offset)
            for point in self.points
        }
        self.locked_top_row += y_offset
        return self

    re_str = re.compile(r"(\| +\|(?:\n\| +\|)+)")

    def __str__(self) -> str:
        return self.re_str.sub(self.sub, super().__str__())

    def sub(self, match: Match) -> str:
        return "|{}|".format(
            str(match.group().count("\n") + 1).ljust(self.width, " "),
        )


Challenge.main()
challenge = Challenge()
