#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from itertools import chain
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, min_and_max_tuples,
)


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """


class AmphipodEnum(Enum):
    Amber = "A"
    Bronze = "B"
    Copper = "C"
    Desert = "D"

    @classmethod
    def all_values(cls) -> Set[str]:
        """
        >>> sorted(AmphipodEnum.all_values())
        ['A', 'B', 'C', 'D']
        """
        return {
            value.value
            for value in cls
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


@dataclass
class Maze:
    walls: Set[Point2D]
    amphipods: Dict[Point2D, AmphipodEnum]

    @classmethod
    def from_maze_text(cls, maze_text: str) -> "Maze":
        """
        >>> maze = Maze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''')
        >>> len(maze.amphipods)
        8
        >>> print(maze)
        #############
        #...........#
        ###A#D#C#A###
        ..#C#D#B#B#..
        ..#########..
        """
        walls = {
            point
            for y, line in enumerate(filter(None, maze_text.splitlines()))
            for x, character in enumerate(line)
            for point in [Point2D(x, y)]
            if character == "#"
        }
        amphipods = cls.parse_amphipods(maze_text)
        (min_x, min_y), (max_x, max_y) = \
            min_and_max_tuples(chain(walls, amphipods))
        if (min_x, max_x) != (0, 0):
            offset = Point2D(-min_x, -max_x)
            walls = set(map(offset.offset, walls))
            amphipods = {
                offset.offset(point): amphipod
                for point, amphipod in amphipods.items()
            }
        return cls(
            walls=walls,
            amphipods=amphipods,
        )

    @classmethod
    def parse_amphipods(cls, maze_text: str) -> Dict[Point2D, AmphipodEnum]:
        """
        >>> len(Maze.parse_amphipods('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... '''))
        8
        """
        amphipod_values = AmphipodEnum.all_values()
        return {
            point: AmphipodEnum(character)
            for y, line in enumerate(filter(None, maze_text.splitlines()))
            for x, character in enumerate(line)
            for point in [Point2D(x, y)]
            if character in amphipod_values
        }

    def __str__(self) -> "str":
        if not self.walls:
            return ""

        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.walls)
        return "\n".join(
            "".join(
                value.value
                if isinstance(value, AmphipodEnum) else
                "#"
                if value else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
                for value in [self[point]]
            )
            for y in range(min_y, max_y + 1)
        )

    def __getitem__(self, item: Point2D) -> Union[bool, AmphipodEnum]:
        if item in self.amphipods:
            return self.amphipods[item]
        return item in self.walls


Challenge.main()
challenge = Challenge()
