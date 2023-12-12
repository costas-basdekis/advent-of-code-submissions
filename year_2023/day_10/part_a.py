#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        7066
        """
        return Field.from_field_text(_input).get_max_distance()


@dataclass
class Field:
    tiles: Dict[Point2D, Optional["PipeType"]]
    starting_position: Point2D

    @classmethod
    def from_field_text(cls, field_text: str) -> "Field":
        """
        >>> Field.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''')
        Field(tiles={...}, starting_position=Point2D(x=1, y=1))
        """
        field_text = field_text.strip().replace(" ", "")
        return cls(
            {
                Point2D(x, y): PipeType.from_tile_text(character)
                for y, line in enumerate(field_text.splitlines())
                for x, character in enumerate(line)
                if character not in (".", "S")
            },
            [
                Point2D(x, y)
                for y, line in enumerate(field_text.splitlines())
                for x, character in enumerate(line)
                if character == "S"
            ][0],
        )

    def get_neighbours(self, position: Point2D) -> List[Point2D]:
        """
        >>> field = Field.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''')
        >>> field.get_neighbours(Point2D(0, 0))
        []
        >>> field.get_neighbours(Point2D(3, 1))
        [Point2D(x=3, y=2), Point2D(x=2, y=1)]
        >>> field.get_neighbours(Point2D(1, 1))
        [Point2D(x=2, y=1), Point2D(x=1, y=2)]
        """
        if position in self.tiles:
            return self.tiles[position].get_neighbours(position)
        return [
            neighbour
            for neighbour in position.get_manhattan_neighbours()
            if neighbour in self.tiles
            and position in self.tiles[neighbour].get_neighbours(neighbour)
        ]

    def get_max_distance(
        self, starting_position: Optional[Point2D] = None,
    ) -> int:
        """
        >>> Field.from_field_text('''
        ...     .....
        ...     .S-7.
        ...     .|.|.
        ...     .L-J.
        ...     .....
        ... ''').get_max_distance()
        4
        >>> Field.from_field_text('''
        ...     ..F7.
        ...     .FJ|.
        ...     SJ.L7
        ...     |F--J
        ...     LJ...
        ... ''').get_max_distance()
        8
        """
        if starting_position is None:
            starting_position = self.starting_position

        seen: Set[Point2D] = {starting_position}
        max_distance_seen = 0
        stack: List[Tuple[Point2D, int]] = [(starting_position, 0)]
        while stack:
            position, distance = stack.pop(0)
            new_distance = distance + 1
            for neighbour in self.get_neighbours(position):
                if neighbour in seen:
                    continue
                seen.add(neighbour)
                stack.append((neighbour, new_distance))
                max_distance_seen = max(max_distance_seen, new_distance)

        return max_distance_seen


class Direction(Enum):
    North = "north", Point2D(0, -1)
    South = "south", Point2D(0, 1)
    West = "west", Point2D(-1, 0)
    East = "east", Point2D(1, 0)

    offset: Point2D

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: str, offset: Point2D):
        self.offset = offset

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class PipeType(Enum):
    NS = "|", (Direction.North, Direction.South)
    WE = "-", (Direction.West, Direction.East)
    NE = "L", (Direction.North, Direction.East)
    NW = "J", (Direction.North, Direction.West)
    SE = "F", (Direction.South, Direction.East)
    SW = "7", (Direction.South, Direction.West)

    directions: Tuple[Direction, Direction]

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    @classmethod
    def from_tile_text(cls, tile_text: str) -> "PipeType":
        return PipeTypeTextMap[tile_text]

    def __init__(self, _: str, directions: Tuple[Direction, Direction]):
        self.directions = directions

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    @property
    def offsets(self) -> Tuple[Point2D, Point2D]:
        first, second = self.directions
        return first.offset, second.offset

    def get_neighbours(self, position: Point2D) -> List[Point2D]:
        return list(map(position.offset, self.offsets))


PipeTypeTextMap: Dict[str, PipeType] = {
    pipe_type.value: pipe_type
    for pipe_type in PipeType
}


Challenge.main()
challenge = Challenge()
