#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from itertools import count
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper,
)


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        563
        """
        return Herd\
            .from_herd_text(_input)\
            .get_stop_move_count(debugger=debugger)


class DirectionEnum(Enum):
    East = "east"
    South = "south"


@dataclass
class Herd:
    cucumbers: Dict[Point2D, Optional[DirectionEnum]]
    size: Point2D

    PARSE_MAP = {
        ">": DirectionEnum.East,
        "v": DirectionEnum.South,
        ":": None,
        ".": None,
    }

    @classmethod
    def from_herd_text(cls, herd_text: str) -> "Herd":
        """
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... '''))
        v...>>.vv>
        .vv>>.vv..
        >>.>v>...v
        >>v>>.>.v.
        v>v.vv.v..
        >.>>..v...
        .vv..>.>v.
        v.v..>>v.v
        ....v..v.>
        >>> print(Herd.from_herd_text('''
        ...     ..........
        ...     .>v....v..
        ...     .......>..
        ...     ..........
        ... '''))
        :.........
        .>v....v..
        .......>..
        ..........
        """
        lines = filter(None, map(str.strip, herd_text.splitlines()))
        cucumbers = {
            Point2D(x, y): cls.PARSE_MAP[character]
            for y, line in enumerate(lines)
            for x, character in enumerate(line)
        }
        return cls(
            cucumbers=cucumbers,
            size=max(cucumbers).offset(Point2D(1, 1)),
        )

    STR_MAP = {
        cucumber: as_string
        for as_string, cucumber in PARSE_MAP.items()
    }

    def __str__(self) -> str:
        as_string = "\n".join(
            "".join(
                self.STR_MAP[self.cucumbers[Point2D(x, y)]]
                for x in range(self.size.x)
            )
            for y in range(self.size.y)
        )
        if as_string[0] == ".":
            as_string = f":{as_string[1:]}"

        return as_string

    def get_stop_move_count(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').get_stop_move_count()
        58
        """
        move_count, _ = self.move_until_stop(debugger=debugger)

        return move_count

    def move_until_stop(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> Tuple[int, "Herd"]:
        """
        >>> _step_count, final = Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move_until_stop()
        >>> _step_count
        58
        >>> print(final)
        :.>>v>vv..
        ..v.>>vv..
        ..>>v>>vv.
        ..>>>>>vv.
        v......>vv
        v>v....>>v
        vvv.....>>
        >vv......>
        .>v.vv.v..
        """
        moved = self
        for step_count in debugger.stepping(count(1)):
            previous = moved
            moved = moved.move()
            debugger.default_report_if("Searching...")
            if moved == previous:
                return step_count, previous

    def move_many(self, step_count: int) -> "Herd":
        """
        >>> print(Herd.from_herd_text('''
        ...     ...>...
        ...     .......
        ...     ......>
        ...     v.....>
        ...     ......>
        ...     .......
        ...     ..vvv..
        ... ''').move_many(4))
        >......
        ..v....
        ..>.v..
        .>.v...
        ...>...
        .......
        v......
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move_many(1))
        :...>.>v.>
        v.v>.>v.v.
        >v>>..>v..
        >>v>v>.>.v
        .>v.v...v.
        v>>.>vvv..
        ..v...>>..
        vv...>>vv.
        >.v.v..v.v
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move_many(2))
        >.v.v>>..v
        v.v.>>vv..
        >v>.>.>.v.
        >>v>v.>v>.
        .>..v....v
        .>v>>.v.v.
        v....v>v>.
        .vv..>>v..
        v>.....vv.
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move_many(5))
        vv>...>v>.
        v.v.v>.>v.
        >.v.>.>.>v
        >v>.>..v>>
        ..v>v.v...
        ..>.>>vvv.
        .>...v>v..
        ..v.v>>v.v
        v.v.>...v.
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move_many(10))
        :.>..>>vv.
        v.....>>.v
        ..v.v>>>v>
        v>.>v.>>>.
        ..v>v.vv.v
        .v.>>>.v..
        v.v..>v>..
        ..v...>v.>
        .vv..v>vv.
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move_many(30))
        :vv.v..>>>
        v>...v...>
        >.v>.>vv.>
        >v>.>.>v.>
        .>..v.vv..
        ..v>..>>v.
        ....v>..>v
        v.v...>vv>
        v.v...>vvv
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move_many(57))
        :.>>v>vv..
        ..v.>>vv..
        ..>>v>>vv.
        ..>>>>>vv.
        v......>vv
        v>v....>>v
        vvv.....>>
        >vv......>
        .>v.vv.v..
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move_many(58))
        :.>>v>vv..
        ..v.>>vv..
        ..>>v>>vv.
        ..>>>>>vv.
        v......>vv
        v>v....>>v
        vvv.....>>
        >vv......>
        .>v.vv.v..
        """
        moved = self
        for _ in range(step_count):
            moved = moved.move()

        return moved

    def move(self) -> "Herd":
        """
        >>> print(Herd.from_herd_text('''
        ...     >...
        ...     ....
        ... ''').move())
        :>..
        ....
        >>> print(Herd.from_herd_text('''
        ...     ..........
        ...     .>v....v..
        ...     .......>..
        ...     ..........
        ... ''').move())
        :.........
        .>........
        ..v....v>.
        ..........
        >>> print(Herd.from_herd_text('''
        ...     ....>.>v.>
        ...     v.v>.>v.v.
        ...     >v>>..>v..
        ...     >>v>v>.>.v
        ...     .>v.v...v.
        ...     v>>.>vvv..
        ...     ..v...>>..
        ...     vv...>>vv.
        ...     >.v.v..v.v
        ... ''').move())
        >.v.v>>..v
        v.v.>>vv..
        >v>.>.>.v.
        >>v>v.>v>.
        .>..v....v
        .>v>>.v.v.
        v....v>v>.
        .vv..>>v..
        v>.....vv.
        >>> print(Herd.from_herd_text('''
        ...     v...>>.vv>
        ...     .vv>>.vv..
        ...     >>.>v>...v
        ...     >>v>>.>.v.
        ...     v>v.vv.v..
        ...     >.>>..v...
        ...     .vv..>.>v.
        ...     v.v..>>v.v
        ...     ....v..v.>
        ... ''').move())
        :...>.>v.>
        v.v>.>v.v.
        >v>>..>v..
        >>v>v>.>.v
        .>v.v...v.
        v>>.>vvv..
        ..v...>>..
        vv...>>vv.
        >.v.v..v.v
        """
        return self.move_east().move_south()

    def move_east(self) -> "Herd":
        return self.move_direction(DirectionEnum.East)

    def move_south(self) -> "Herd":
        return self.move_direction(DirectionEnum.South)

    OFFSET_MAP = {
        DirectionEnum.East: Point2D(1, 0),
        DirectionEnum.South: Point2D(0, 1),
    }

    def move_direction(self, direction: DirectionEnum) -> "Herd":
        offset = self.OFFSET_MAP[direction]
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            cucumbers={
                point: (
                    None
                    if (
                        self.cucumbers[point] == direction
                        and self.cucumbers[next_point] is None
                    ) else
                    self.cucumbers[previous_point]
                    if (
                        self.cucumbers[point] is None
                        and self.cucumbers[previous_point] == direction
                    ) else
                    self.cucumbers[point]
                )
                for y in range(self.size.y)
                for x in range(self.size.x)
                for point in [Point2D(x, y)]
                for next_point in [self.get_next_point(point, offset)]
                for previous_point in [self.get_previous_point(point, offset)]
            },
            size=self.size,
        )

    def get_previous_point(self, point: Point2D, offset: Point2D) -> Point2D:
        return Point2D(
            (point.x - offset.x) % self.size.x,
            (point.y - offset.y) % self.size.y,
        )

    def get_next_point(self, point: Point2D, offset: Point2D) -> Point2D:
        return Point2D(
            (point.x + offset.x) % self.size.x,
            (point.y + offset.y) % self.size.y,
        )


Challenge.main()
challenge = Challenge()
