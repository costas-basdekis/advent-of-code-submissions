#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Iterable, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples
from year_2022.day_14 import part_a
from year_2022.day_14.part_a import WallMap, FilledUpException


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        27426
        """
        _map = WallMapExtended.from_walls_text(_input)
        drop_count = _map.drop_all_sands()
        if debugger:
            debugger.report(_map.render_with_next_path())
        return drop_count


@dataclass
class WallMapExtended(WallMap):
    """
    >>> _map = WallMapExtended.from_walls_text(
    ...     "498,4 -> 498,6 -> 496,6\\n"
    ...     "503,4 -> 502,4 -> 502,9 -> 494,9"
    ... )
    >>> print(":" + str(_map))
    :......+...
    ..........
    ..........
    ..........
    ....#...##
    ....#...#.
    ..###...#.
    ........#.
    ........#.
    #########.
    ..........
    ##########
    >>> _map.drop_all_sands()
    93
    >>> print(":" + str(_map))
    :..........o..........
    .........ooo.........
    ........ooooo........
    .......ooooooo.......
    ......oo#ooo##o......
    .....ooo#ooo#ooo.....
    ....oo###ooo#oooo....
    ...oooo.oooo#ooooo...
    ..oooooooooo#oooooo..
    .ooo#########ooooooo.
    ooooo.......ooooooooo
    #####################
    """
    bottom_row_y: int = field(default=-1)

    def __post_init__(self):
        if self.bottom_row_y == -1:
            _, (_, max_y) = self.min_and_max_walls
            self.bottom_row_y = max_y + 2
            self.min_and_max_walls = min_and_max_tuples(
                self.walls
                | {self.center, Point2D(self.center.x, self.bottom_row_y)}
                | self.sand
            )

    def render_point(self, point: Point2D, next_path: Set[Point2D]) -> str:
        if point.y == self.bottom_row_y:
            return "#"
        return super().render_point(point, next_path)

    def __getitem__(self, item: Point2D) -> bool:
        if item.y == self.bottom_row_y:
            return True
        return super().__getitem__(item)

    def __setitem__(self, key: Point2D, value: bool) -> None:
        if key.y == self.bottom_row_y:
            raise Exception(f"Can't change walls")
        super().__setitem__(key, value)
        (min_x, min_y), (max_x, max_y) = self.min_and_max_walls
        if key.x < min_x:
            self.min_and_max_walls = (key.x, min_y), (max_x, max_y)
        elif key.x > max_x:
            self.min_and_max_walls = (min_x, min_y), (key.x, max_y)

    def iterate_next_sand_path(self) -> Iterable[Point2D]:
        try:
            yield from super().iterate_next_sand_path()
        except FilledUpException:
            if not self[self.center]:
                yield self.center


Challenge.main()
challenge = Challenge()
