#!/usr/bin/env python3
import itertools
from dataclasses import dataclass, field
from typing import ClassVar, Iterable, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D,  min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        779
        """
        _map = WallMap.from_walls_text(_input)
        drop_count = _map.drop_all_sands()
        if debugger:
            debugger.report(_map.render_with_next_path())
        return drop_count


@dataclass
class WallMap:
    walls: Set[Point2D]
    min_and_max_walls: Tuple[Tuple[int, int], Tuple[int, int]]
    sand: Set[Point2D] = field(default_factory=set)
    default_center: ClassVar[Point2D] = Point2D(500, 0)
    center: Point2D = field(default=default_center)

    @classmethod
    def from_walls_text(cls, walls_text: str) -> "WallMap":
        """
        >>> print(":" + str(WallMap.from_walls_text(
        ...     "498,4 -> 498,6 -> 496,6\\n"
        ...     "503,4 -> 502,4 -> 502,9 -> 494,9"
        ... )))
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
        """
        walls = set()
        for line in walls_text.strip().splitlines():
            coordinates_str = line.split(" -> ")
            coordinates = list(map(cls.parse_coordinates, coordinates_str))
            coordinates_pairs = zip(coordinates, coordinates[1:])
            for start, end in coordinates_pairs:
                if start.x == end.x:
                    x = start.x
                    ys = range(min(start.y, end.y), max(start.y, end.y) + 1)
                    for y in ys:
                        walls.add(Point2D(x, y))
                elif start.y == end.y:
                    xs = range(min(start.x, end.x), max(start.x, end.x) + 1)
                    y = start.y
                    for x in xs:
                        walls.add(Point2D(x, y))
                else:
                    raise Exception(
                        f"Wall {start} -> {end} is not horizontal or verticall"
                    )
        return cls.from_walls(walls)

    @classmethod
    def from_walls(cls, walls: Set[Point2D]) -> "WallMap":
        return cls(
            walls=walls,
            min_and_max_walls=min_and_max_tuples(walls | {cls.default_center}),
        )

    @classmethod
    def parse_coordinates(cls, coordinates_str: str) -> Point2D:
        """
        >>> WallMap.parse_coordinates("477,140")
        Point2D(x=477, y=140)
        """
        x_str, y_str = coordinates_str.split(",")
        return Point2D(int(x_str), int(y_str))

    def __str__(self, show_next_path: bool = False) -> str:
        """
        >>> print(str(WallMap.from_walls(set())))
        +
        """
        if show_next_path:
            next_path = set(self.iterate_next_sand_path())
            (min_x, min_y), (max_x, max_y) = \
                min_and_max_tuples(self.walls | {self.center} | next_path)
        else:
            next_path = set()
            (min_x, min_y), (max_x, max_y) = self.min_and_max_walls
        return "\n".join(
            "".join(
                "+"
                if point == self.center else
                "~"
                if point in next_path else
                "#"
                if point in self.walls else
                "o"
                if point in self.sand else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    def render_with_next_path(self) -> str:
        return self.__str__(True)

    next_offsets: ClassVar[List[Point2D]] = [
        Point2D(0, 1),
        Point2D(-1, 1),
        Point2D(1, 1),
    ]

    def drop_all_sands(self) -> int:
        """
        >>> _map = WallMap.from_walls_text(
        ...     "498,4 -> 498,6 -> 496,6\\n"
        ...     "503,4 -> 502,4 -> 502,9 -> 494,9"
        ... )
        >>> _map.drop_all_sands()
        24
        >>> print(":" + str(_map))
        :......+...
        ..........
        ......o...
        .....ooo..
        ....#ooo##
        ...o#ooo#.
        ..###ooo#.
        ....oooo#.
        .o.ooooo#.
        #########.
        >>> print(":" + _map.render_with_next_path())
        :.......+...
        .......~...
        ......~o...
        .....~ooo..
        ....~#ooo##
        ...~o#ooo#.
        ..~###ooo#.
        ..~..oooo#.
        .~o.ooooo#.
        ~#########.
        ~..........
        """
        for amount in itertools.count():
            if not self.drop_one_sand():
                return amount
        raise Exception(f"Exited infinite loop")

    def drop_many_sands(self, count: int) -> int:
        """
        >>> _map = WallMap.from_walls_text(
        ...     "498,4 -> 498,6 -> 496,6\\n"
        ...     "503,4 -> 502,4 -> 502,9 -> 494,9"
        ... )
        >>> _map.drop_one_sand()
        True
        >>> print(":" + str(_map))
        :......+...
        ..........
        ..........
        ..........
        ....#...##
        ....#...#.
        ..###...#.
        ........#.
        ......o.#.
        #########.
        >>> _map.drop_many_sands(23)
        23
        >>> print(":" + str(_map))
        :......+...
        ..........
        ......o...
        .....ooo..
        ....#ooo##
        ...o#ooo#.
        ..###ooo#.
        ....oooo#.
        .o.ooooo#.
        #########.
        >>> print(":" + _map.render_with_next_path())
        :.......+...
        .......~...
        ......~o...
        .....~ooo..
        ....~#ooo##
        ...~o#ooo#.
        ..~###ooo#.
        ..~..oooo#.
        .~o.ooooo#.
        ~#########.
        ~..........
        >>> _map.drop_one_sand()
        False
        >>> _map.drop_many_sands(23)
        0
        >>> print(":" + str(_map))
        :......+...
        ..........
        ......o...
        .....ooo..
        ....#ooo##
        ...o#ooo#.
        ..###ooo#.
        ....oooo#.
        .o.ooooo#.
        #########.
        >>> print(":" + _map.render_with_next_path())
        :.......+...
        .......~...
        ......~o...
        .....~ooo..
        ....~#ooo##
        ...~o#ooo#.
        ..~###ooo#.
        ..~..oooo#.
        .~o.ooooo#.
        ~#########.
        ~..........
        """
        for amount in range(count):
            if not self.drop_one_sand():
                return amount

        return count

    def drop_one_sand(self) -> bool:
        next_position = self.get_next_sand_position()
        if not next_position:
            return False
        self[next_position] = True
        return True

    def get_next_sand_position(self) -> Optional[Point2D]:
        next_position: Optional[Point2D] = None
        for position in self.iterate_next_sand_path():
            next_position = position
        if not next_position:
            return None
        _, (_, max_y) = self.min_and_max_walls
        if next_position.y > max_y:
            return None
        return next_position

    def iterate_next_sand_path(self) -> Iterable[Point2D]:
        _, (_, max_y) = self.min_and_max_walls
        position = self.center
        while True:
            for next_offset in self.next_offsets:
                next_position = position.offset(next_offset)
                if not self[next_position]:
                    break
            else:
                break
            yield next_position
            position = next_position
            if position.y > max_y:
                break
        if position == self.center:
            raise Exception(f"Sand has nowhere to go")

    def __getitem__(self, item: Point2D) -> bool:
        return item in self.walls or item in self.sand

    def __setitem__(self, key: Point2D, value: bool) -> None:
        if not self[key]:
            if value:
                self.sand.add(key)
        else:
            if key in self.walls:
                raise Exception(f"Can't change walls")
            if value:
                self.sand.add(key)
            else:
                if key in self.sand:
                    self.sand.remove(key)


Challenge.main()
challenge = Challenge()
