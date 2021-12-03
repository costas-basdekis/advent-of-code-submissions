#!/usr/bin/env python3
from functools import cached_property

from itertools import combinations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, iterable_length
from year_2021.day_23.part_a import AmphipodEnum


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        52055
        """
        return DeepMaze\
            .from_maze_text(_input)\
            .find_minimum_cost_to_organise(debugger=debugger)


class DeepPositionNameEnum(Enum):
    Corridor1 = "1"
    Corridor2 = "2"
    Corridor3 = "3"
    Corridor4 = "4"
    Corridor5 = "5"
    Corridor6 = "6"
    Corridor7 = "7"
    A1 = "A"
    A2 = "a"
    A3 = "X"
    A4 = "x"
    B1 = "B"
    B2 = "b"
    B3 = "Y"
    B4 = "y"
    C1 = "C"
    C2 = "c"
    C3 = "Z"
    C4 = "z"
    D1 = "D"
    D2 = "d"
    D3 = "W"
    D4 = "w"

    @classmethod
    def from_position(cls, position: Point2D) -> "DeepPositionNameEnum":
        """
        >>> DeepPositionNameEnum.from_position(Point2D(x=1, y=1))
        DeepPositionNameEnum.Corridor1
        >>> DeepPositionNameEnum.from_position(Point2D(x=2, y=1))
        DeepPositionNameEnum.Corridor2
        >>> DeepPositionNameEnum.from_position(Point2D(x=3, y=2))
        DeepPositionNameEnum.A4
        >>> DeepPositionNameEnum.from_position(Point2D(x=3, y=3))
        DeepPositionNameEnum.A3
        >>> DeepPositionNameEnum.from_position(Point2D(x=3, y=4))
        DeepPositionNameEnum.A2
        >>> DeepPositionNameEnum.from_position(Point2D(x=3, y=5))
        DeepPositionNameEnum.A1
        """
        position_name = cls.maybe_from_position(position)
        if not position_name:
            raise Exception(f"No position name for {position}")
        return position_name

    @classmethod
    def maybe_from_position(
        cls, position: Point2D,
    ) -> Optional["DeepPositionNameEnum"]:
        """
        >>> DeepPositionNameEnum.maybe_from_position(Point2D(x=1, y=1))
        DeepPositionNameEnum.Corridor1
        >>> DeepPositionNameEnum.maybe_from_position(Point2D(x=2, y=1))
        DeepPositionNameEnum.Corridor2
        >>> DeepPositionNameEnum.maybe_from_position(Point2D(x=3, y=2))
        DeepPositionNameEnum.A4
        >>> DeepPositionNameEnum.maybe_from_position(Point2D(x=3, y=3))
        DeepPositionNameEnum.A3
        >>> DeepPositionNameEnum.maybe_from_position(Point2D(x=3, y=4))
        DeepPositionNameEnum.A2
        >>> DeepPositionNameEnum.maybe_from_position(Point2D(x=3, y=5))
        DeepPositionNameEnum.A1
        >>> DeepPositionNameEnum.maybe_from_position(Point2D(x=0, y=0))
        """
        try:
            return cls(cls.MAZE_LINES[position.y][position.x])
        except ValueError:
            return None

    @classmethod
    def get_rooms(cls) -> Set["DeepPositionNameEnum"]:
        """
        >>> sorted(DeepPositionNameEnum.get_rooms())
        [DeepPositionNameEnum.A1, DeepPositionNameEnum.A2,
            DeepPositionNameEnum.A3, DeepPositionNameEnum.A4,
            DeepPositionNameEnum.B1, DeepPositionNameEnum.B2,
            DeepPositionNameEnum.B3, DeepPositionNameEnum.B4,
            DeepPositionNameEnum.C1, DeepPositionNameEnum.C2,
            DeepPositionNameEnum.C3, DeepPositionNameEnum.C4,
            DeepPositionNameEnum.D1, DeepPositionNameEnum.D2,
            DeepPositionNameEnum.D3, DeepPositionNameEnum.D4]
        """
        return {
            position
            for position in cls
            if not position.is_corridor
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __lt__(self, other: "DeepPositionNameEnum") -> bool:
        return self.name < other.name

    MAZE_LINES: List[str]

    # noinspection DuplicatedCode
    @cached_property
    def position(self) -> Point2D:
        """
        >>> DeepPositionNameEnum.Corridor1.position
        Point2D(x=1, y=1)
        >>> DeepPositionNameEnum.Corridor2.position
        Point2D(x=2, y=1)
        >>> DeepPositionNameEnum.A4.position
        Point2D(x=3, y=2)
        >>> DeepPositionNameEnum.A3.position
        Point2D(x=3, y=3)
        >>> DeepPositionNameEnum.A2.position
        Point2D(x=3, y=4)
        >>> DeepPositionNameEnum.A1.position
        Point2D(x=3, y=5)
        """
        matched_lines = [
            (y, line)
            for y, line in enumerate(self.MAZE_LINES)
            if self.value in line
        ]
        if len(matched_lines) != 1:
            raise ValueError(f"Could not find line with '{self.value}'")
        (y, line), = matched_lines
        return Point2D(line.index(self.value), y)

    _DISTANCE_TO_CACHE: Dict[
        Tuple["DeepPositionNameEnum", "DeepPositionNameEnum"],
        Union[Exception, int],
    ]

    def get_distance_to(self, other: "DeepPositionNameEnum") -> int:
        """
        >>> DeepPositionNameEnum.A1\\
        ...     .get_distance_to(DeepPositionNameEnum.Corridor1)
        6
        >>> DeepPositionNameEnum.A1\\
        ...     .get_distance_to(DeepPositionNameEnum.B1)
        10
        >>> DeepPositionNameEnum.A1\\
        ...     .get_distance_to(DeepPositionNameEnum.B2)
        9
        >>> DeepPositionNameEnum.A1\\
        ...     .get_distance_to(DeepPositionNameEnum.A2)
        1
        >>> DeepPositionNameEnum.A1\\
        ...     .get_distance_to(DeepPositionNameEnum.A1)
        0
        """
        if (self, other) not in self._DISTANCE_TO_CACHE:
            self._DISTANCE_TO_CACHE[(self, other)] \
                = self._DISTANCE_TO_CACHE[(other, self)] \
                = self._get_distance_to(other)

        return self._DISTANCE_TO_CACHE[(self, other)]

    # noinspection DuplicatedCode
    def _get_distance_to(
        self, other: "DeepPositionNameEnum",
    ) -> Union[Exception, int]:
        if self.is_corridor and other.is_corridor:
            return ValueError(
                f"Cannot move between two corridors {self} to {other}"
            )
        position = self.position
        if not self.is_corridor and not other.is_corridor:
            if position.x != other.position.x:
                return (
                    position.y - self.Corridor1.position.y
                    + other.position.y - self.Corridor1.position.y
                    + abs(position.x - other.position.x)
                )
        return position.manhattan_distance(other.position)

    @cached_property
    def is_corridor(self) -> bool:
        """
        >>> DeepPositionNameEnum.A1.is_corridor
        False
        >>> DeepPositionNameEnum.Corridor1.is_corridor
        True
        """
        return "Corridor" in self.name

    @cached_property
    def is_inner(self) -> bool:
        """
        >>> DeepPositionNameEnum.A1.is_inner
        True
        >>> DeepPositionNameEnum.A2.is_inner
        False
        >>> DeepPositionNameEnum.Corridor1.is_inner
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if self.is_corridor:
            raise ValueError(f"{self} is a corridor")
        return "1" in self.name

    @cached_property
    def inner(self) -> "DeepPositionNameEnum":
        """
        >>> DeepPositionNameEnum.A1.inner
        DeepPositionNameEnum.A1
        >>> DeepPositionNameEnum.A2.inner
        DeepPositionNameEnum.A1
        >>> DeepPositionNameEnum.Corridor1.inner
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if self.is_inner:
            return self

        return type(self)(self.name[0])

    @cached_property
    def inner_ones(self) -> List["DeepPositionNameEnum"]:
        """
        >>> DeepPositionNameEnum.A1.inner_ones
        []
        >>> DeepPositionNameEnum.A2.inner_ones
        [DeepPositionNameEnum.A1]
        >>> DeepPositionNameEnum.A3.inner_ones
        [DeepPositionNameEnum.A1, DeepPositionNameEnum.A2]
        >>> DeepPositionNameEnum.A4.inner_ones
        [DeepPositionNameEnum.A1, DeepPositionNameEnum.A2,
            DeepPositionNameEnum.A3]
        >>> DeepPositionNameEnum.Corridor1.inner_ones
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if self.is_inner:
            return []

        cls = type(self)
        return [
            getattr(cls, f"{self.name[0]}1")
        ] + [
            getattr(cls, f"{self.name[0]}{i}")
            for i in range(2, int(self.name[1]))
        ]

    @cached_property
    def outer_ones(self) -> List["DeepPositionNameEnum"]:
        """
        >>> DeepPositionNameEnum.A1.outer_ones
        [DeepPositionNameEnum.A2, DeepPositionNameEnum.A3,
            DeepPositionNameEnum.A4]
        >>> DeepPositionNameEnum.A2.outer_ones
        [DeepPositionNameEnum.A3, DeepPositionNameEnum.A4]
        >>> DeepPositionNameEnum.A3.outer_ones
        [DeepPositionNameEnum.A4]
        >>> DeepPositionNameEnum.A4.outer_ones
        []
        >>> DeepPositionNameEnum.Corridor1.outer_ones
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        cls = type(self)
        return [
            getattr(cls, f"{self.name[0]}{i}")
            for i in range(int(self.name[1]) + 1, 5)
        ]

    @cached_property
    def amphipod(self) -> AmphipodEnum:
        """
        >>> DeepPositionNameEnum.A1.amphipod
        AmphipodEnum.A
        >>> DeepPositionNameEnum.A2.amphipod
        AmphipodEnum.A
        >>> DeepPositionNameEnum.Corridor1.amphipod
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if self.is_corridor:
            raise ValueError(f"{self} is not a room")
        return AmphipodEnum(self.name[0])

    _POSITION_NAMES_BETWEEN_CACHE: Dict[
        Tuple["DeepPositionNameEnum", "DeepPositionNameEnum"],
        Union[Exception, List["DeepPositionNameEnum"]],
    ]

    def get_position_names_between(
        self, other: "DeepPositionNameEnum",
    ) -> List["DeepPositionNameEnum"]:
        """
        >>> DeepPositionNameEnum.A1\\
        ...     .get_position_names_between(DeepPositionNameEnum.Corridor1)
        [DeepPositionNameEnum.A2, DeepPositionNameEnum.A3,
            DeepPositionNameEnum.A4, DeepPositionNameEnum.Corridor1,
            DeepPositionNameEnum.Corridor2]
        >>> DeepPositionNameEnum.A2\\
        ...     .get_position_names_between(DeepPositionNameEnum.Corridor1)
        [DeepPositionNameEnum.A3, DeepPositionNameEnum.A4,
            DeepPositionNameEnum.Corridor1, DeepPositionNameEnum.Corridor2]
        >>> DeepPositionNameEnum.A3\\
        ...     .get_position_names_between(DeepPositionNameEnum.Corridor1)
        [DeepPositionNameEnum.A4, DeepPositionNameEnum.Corridor1,
            DeepPositionNameEnum.Corridor2]
        >>> DeepPositionNameEnum.A4\\
        ...     .get_position_names_between(DeepPositionNameEnum.Corridor1)
        [DeepPositionNameEnum.Corridor1, DeepPositionNameEnum.Corridor2]
        >>> DeepPositionNameEnum.A1\\
        ...     .get_position_names_between(DeepPositionNameEnum.Corridor5)
        [DeepPositionNameEnum.A2, DeepPositionNameEnum.A3,
            DeepPositionNameEnum.A4, DeepPositionNameEnum.Corridor3,
            DeepPositionNameEnum.Corridor4, DeepPositionNameEnum.Corridor5]
        >>> DeepPositionNameEnum.C4\\
        ...     .get_position_names_between(DeepPositionNameEnum.Corridor2)
        [DeepPositionNameEnum.Corridor2,
            DeepPositionNameEnum.Corridor3, DeepPositionNameEnum.Corridor4]
        >>> DeepPositionNameEnum.Corridor1\\
        ...     .get_position_names_between(DeepPositionNameEnum.A1)
        [DeepPositionNameEnum.A1, DeepPositionNameEnum.A2,
            DeepPositionNameEnum.A3, DeepPositionNameEnum.A4,
            DeepPositionNameEnum.Corridor2]
        >>> DeepPositionNameEnum.Corridor1\\
        ...     .get_position_names_between(DeepPositionNameEnum.A4)
        [DeepPositionNameEnum.A4, DeepPositionNameEnum.Corridor2]
        >>> DeepPositionNameEnum.Corridor5\\
        ...     .get_position_names_between(DeepPositionNameEnum.A1)
        [DeepPositionNameEnum.A1, DeepPositionNameEnum.A2,
            DeepPositionNameEnum.A3, DeepPositionNameEnum.A4,
            DeepPositionNameEnum.Corridor3, DeepPositionNameEnum.Corridor4]
        >>> DeepPositionNameEnum.Corridor2\\
        ...     .get_position_names_between(DeepPositionNameEnum.C4)
        [DeepPositionNameEnum.C4, DeepPositionNameEnum.Corridor3,
            DeepPositionNameEnum.Corridor4]
        >>> DeepPositionNameEnum.A1\\
        ...     .get_position_names_between(DeepPositionNameEnum.A4)
        [DeepPositionNameEnum.A2, DeepPositionNameEnum.A3,
            DeepPositionNameEnum.A4]
        >>> DeepPositionNameEnum.A4\\
        ...     .get_position_names_between(DeepPositionNameEnum.A1)
        [DeepPositionNameEnum.A1, DeepPositionNameEnum.A2,
            DeepPositionNameEnum.A3]
        """
        if (self, other) not in self._POSITION_NAMES_BETWEEN_CACHE:
            self._POSITION_NAMES_BETWEEN_CACHE[(self, other)] = \
                self._get_position_names_between(other)

        return self._POSITION_NAMES_BETWEEN_CACHE[(self, other)]

    def _get_position_names_between(
        self, other: "DeepPositionNameEnum",
    ) -> List["DeepPositionNameEnum"]:
        # noinspection DuplicatedCode
        if self.is_corridor and other.is_corridor:
            raise ValueError(
                "Cannot get position names between two on the corridor "
                "({self} and {other})"
            )

        cls = type(self)
        if not self.is_corridor and not other.is_corridor:
            if self.position.x == other.position.x:
                start_i = int(self.name[1])
                end_i = int(other.name[1])
                if start_i < end_i:
                    i_s = range(start_i + 1, end_i + 1)
                else:
                    i_s = range(end_i, start_i)
                return [
                    getattr(cls, f"{self.name[0]}{i}")
                    for i in i_s
                ]
            middle = cls(str(int(self.room_number + other.room_number) // 2))
            return (
                self.get_position_names_between(middle)
                + middle.get_position_names_between(other)
            )

        if self.is_corridor:
            corridor, room = self, other
        else:
            corridor, room = other, self

        position_names_between = [room]
        position_names_between.extend(room.outer_ones)

        # noinspection DuplicatedCode
        room_number = room.room_number
        corridor_number = corridor.corridor_number
        if room_number < corridor_number:
            min_number, max_number = math.ceil(room_number), corridor_number + 1
        else:
            min_number, max_number = corridor_number, math.ceil(room_number)

        for number in range(min_number, max_number):
            position_names_between.append(cls(str(number)))
        if self in position_names_between:
            position_names_between.remove(self)

        return position_names_between

    ROOM_NUMBER_MAP: Dict["DeepPositionNameEnum", float]

    @cached_property
    def room_number(self) -> float:
        """
        >>> DeepPositionNameEnum.A1.room_number
        2.5
        >>> DeepPositionNameEnum.A2.room_number
        2.5
        >>> DeepPositionNameEnum.A3.room_number
        2.5
        >>> DeepPositionNameEnum.A4.room_number
        2.5
        >>> DeepPositionNameEnum.D1.room_number
        5.5
        >>> DeepPositionNameEnum.D2.room_number
        5.5
        >>> DeepPositionNameEnum.Corridor1.room_number
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if self.is_corridor:
            raise ValueError(f"{self} is not a room")
        return self.ROOM_NUMBER_MAP[self]

    @cached_property
    def corridor_number(self) -> int:
        """
        >>> DeepPositionNameEnum.Corridor1.corridor_number
        1
        >>> DeepPositionNameEnum.Corridor5.corridor_number
        5
        >>> DeepPositionNameEnum.A1.corridor_number
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if not self.is_corridor:
            raise ValueError(
                f"Cannot get corridor number of non-corridor ({self})"
            )

        return int(self.value)


DeepPositionNameEnum.MAZE_LINES = list(filter(None, """
    #############
    #12.3.4.5.67#
    ###x#y#z#w###
    ..#X#Y#Z#W#..
    ..#a#b#c#d#..
    ..#A#B#C#D#..
    ..#########..
""".replace(" ", "").splitlines()))

DeepPositionNameEnum.ROOM_NUMBER_MAP = {
    DeepPositionNameEnum.A1: 2.5,
    DeepPositionNameEnum.A2: 2.5,
    DeepPositionNameEnum.A3: 2.5,
    DeepPositionNameEnum.A4: 2.5,
    DeepPositionNameEnum.B1: 3.5,
    DeepPositionNameEnum.B2: 3.5,
    DeepPositionNameEnum.B3: 3.5,
    DeepPositionNameEnum.B4: 3.5,
    DeepPositionNameEnum.C1: 4.5,
    DeepPositionNameEnum.C2: 4.5,
    DeepPositionNameEnum.C3: 4.5,
    DeepPositionNameEnum.C4: 4.5,
    DeepPositionNameEnum.D1: 5.5,
    DeepPositionNameEnum.D2: 5.5,
    DeepPositionNameEnum.D3: 5.5,
    DeepPositionNameEnum.D4: 5.5,
}

DeepPositionNameEnum._DISTANCE_TO_CACHE = {}
DeepPositionNameEnum._POSITION_NAMES_BETWEEN_CACHE = {}


@dataclass
class DeepMaze:
    amphipod_map: Dict[DeepPositionNameEnum, AmphipodEnum]

    @classmethod
    def from_maze_text(cls, maze_text: str) -> "DeepMaze":
        """
        >>> maze = DeepMaze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''')
        >>> len(maze.amphipod_map)
        16
        >>> print(maze)
        #############
        #...........#
        ###A#D#C#A###
        ..#D#C#B#A#..
        ..#D#B#A#C#..
        ..#C#D#B#B#..
        ..#########..
        """
        lines = cls.trim_maze(maze_text)
        return cls(
            amphipod_map={
                position_name: AmphipodEnum(lines[position.y][position.x])
                for position_name in DeepPositionNameEnum.get_rooms()
                for position in [position_name.position]
            },
        )

    @classmethod
    def trim_maze(cls, maze_text: str) -> List[str]:
        """
        >>> print("\\n".join(DeepMaze.trim_maze('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''')))
        #############
        #...........#
        ###A#D#C#A###
          #D#C#B#A#
          #D#B#A#C#
          #C#D#B#B#
          #########
        """
        lines = [
            line.rstrip()
            for line in maze_text.splitlines()
            if line.strip()
        ]
        prefix_length = len(lines[0]) - len(lines[0].lstrip())
        lines = [
            line[prefix_length:]
            for line in lines
        ]
        lines = lines[:3] + [
            "  #D#C#B#A#  ",
            "  #D#B#A#C#  ",
        ] + lines[3:]
        return lines

    # noinspection DuplicatedCode
    def __str__(self) -> "str":
        return "\n".join(
            "".join(
                self.amphipod_map[position_name].value
                if position_name in self.amphipod_map else
                "#"
                if character == "#" else
                "."
                for x, character in enumerate(line)
                for position in [Point2D(x, y)]
                for position_name
                in [DeepPositionNameEnum.maybe_from_position(position)]
            )
            for y, line in enumerate(DeepPositionNameEnum.MAZE_LINES)
        )

    def __hash__(self) -> int:
        """
        >>> maze_a = DeepMaze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''')
        >>> maze_b = DeepMaze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''')
        >>> maze_b in {maze_a: 0}
        True
        """
        return hash(tuple(sorted(self.amphipod_map.items())))

    @property
    def finished(self) -> bool:
        """
        >>> DeepMaze({}).finished
        True
        >>> DeepMaze({
        ...     DeepPositionNameEnum.Corridor1: AmphipodEnum.A,
        ... }).finished
        False
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ... }).finished
        True
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... }).finished
        False
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ...     DeepPositionNameEnum.Corridor1: AmphipodEnum.A,
        ... }).finished
        False
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.B,
        ... }).finished
        False
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... }).finished
        False
        >>> DeepMaze({
        ...     DeepPositionNameEnum.B1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... }).finished
        False
        >>> DeepMaze({
        ...     DeepPositionNameEnum.B1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ... }).finished
        True
        """
        return all(
            not position_name.is_corridor
            and self.is_position_name_finished(position_name)
            for position_name in self.amphipod_map
        )

    @property
    def finish_count(self) -> int:
        """
        >>> DeepMaze({}).finish_count
        0
        >>> DeepMaze({
        ...     DeepPositionNameEnum.Corridor1: AmphipodEnum.A,
        ... }).finish_count
        0
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ... }).finish_count
        1
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... }).finish_count
        0
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ...     DeepPositionNameEnum.Corridor1: AmphipodEnum.A,
        ... }).finish_count
        1
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.B,
        ... }).finish_count
        1
        >>> DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... }).finish_count
        0
        >>> DeepMaze({
        ...     DeepPositionNameEnum.B1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... }).finish_count
        1
        >>> DeepMaze({
        ...     DeepPositionNameEnum.B1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ... }).finish_count
        2
        """
        return iterable_length(filter(None, (
            not position_name.is_corridor
            and self.is_position_name_finished(position_name)
            for position_name in self.amphipod_map
        )))

    # noinspection DuplicatedCode
    def find_minimum_cost_to_organise(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> DeepMaze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###B#C#B#D###
        ...       #A#D#C#A#
        ...       #########
        ... ''').find_minimum_cost_to_organise()
        44169
        """
        stack = [(0, 0, self)]
        seen_cost = {self: 0}
        min_cost: Optional[int] = None
        while debugger.step_if(stack):
            move_count, cost, maze = stack.pop(0)
            if seen_cost[maze] < cost:
                continue
            next_move_count = move_count + 1
            next_stack = []
            for move_cost, next_maze in maze.get_next_moves():
                next_cost = cost + move_cost
                if seen_cost.get(next_maze, next_cost + 1) <= next_cost:
                    continue
                if min_cost is not None and min_cost <= next_cost:
                    continue
                next_stack.append((next_move_count, next_cost, next_maze))
            if not next_stack:
                continue
            max_next_finish_count = max(
                next_maze.finish_count
                for _, _, next_maze in next_stack
            )
            for next_move_count, next_cost, next_maze in next_stack:
                if next_maze.finish_count < max_next_finish_count:
                    continue
                if next_maze.finished:
                    min_cost = next_cost
                    continue
                stack.append((next_move_count, next_cost, next_maze))
                seen_cost[next_maze] = next_cost
            if debugger.should_report():
                debugger.default_report(
                    f"{len(stack)} in stack, seen {len(seen_cost)}, "
                    f"last move count is {move_count}, last cost is {cost}, "
                    f"min cost is {min_cost}, last maze is:\n{maze}\n"
                )
        debugger.default_report(
            f"{len(stack)} in stack, seen {len(seen_cost)}, "
            f"min cost is {min_cost}"
        )

        if min_cost is None:
            raise Exception(f"Could not find end state")

        return min_cost

    def get_next_moves(self) -> Iterable[Tuple[int, "DeepMaze"]]:
        for start, end in self.get_next_trips():
            yield self.get_cost_for(start, end), self.move(start, end)

    def get_next_trips(
        self,
    ) -> Iterable[Tuple[DeepPositionNameEnum, DeepPositionNameEnum]]:
        """
        >>> list(DeepMaze({}).get_next_trips())
        []
        """
        for first, second in combinations(DeepPositionNameEnum, 2):
            if self.can_move_to(first, second):
                yield first, second
            elif self.can_move_to(second, first):
                yield second, first

    def get_cost_for(
        self, start: DeepPositionNameEnum, end: DeepPositionNameEnum,
    ) -> int:
        return start.get_distance_to(end) * self.amphipod_map[start].move_cost

    def move(
        self, start: DeepPositionNameEnum, end: DeepPositionNameEnum,
    ) -> "DeepMaze":
        """
        >>> print(DeepMaze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''').move(
        ...     DeepPositionNameEnum.A4, DeepPositionNameEnum.Corridor1,
        ... ))
        #############
        #A..........#
        ###.#D#C#A###
        ..#D#C#B#A#..
        ..#D#B#A#C#..
        ..#C#D#B#B#..
        ..#########..
        >>> print(DeepMaze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''').move(
        ...     DeepPositionNameEnum.B4, DeepPositionNameEnum.Corridor7,
        ... ))
        #############
        #..........D#
        ###A#.#C#A###
        ..#D#C#B#A#..
        ..#D#B#A#C#..
        ..#C#D#B#B#..
        ..#########..
        """
        amphipod = self.amphipod_map[start]
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            amphipod_map={
                **{
                    position_name: amphipod
                    for position_name, amphipod in self.amphipod_map.items()
                    if position_name != start
                },
                end: amphipod,
            },
        )

    def can_move_to(
        self, start: DeepPositionNameEnum, end: DeepPositionNameEnum,
    ) -> bool:
        """
        >>> maze = DeepMaze({})
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A1, DeepPositionNameEnum.Corridor1,
        ... )
        False
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ... })
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A1, DeepPositionNameEnum.Corridor1,
        ... )
        False
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.B,
        ... })
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A1, DeepPositionNameEnum.Corridor1,
        ... )
        True
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.B,
        ... })
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.Corridor1,
        ... )
        True
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A1, DeepPositionNameEnum.Corridor1,
        ... )
        False
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.B,
        ...     DeepPositionNameEnum.Corridor2: AmphipodEnum.A,
        ... })
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.Corridor1,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.Corridor2,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.Corridor3,
        ... )
        True
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.B1,
        ... )
        True
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.B4,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.C1,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.C4,
        ... )
        False
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.Corridor2: AmphipodEnum.B,
        ... })
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.Corridor2, DeepPositionNameEnum.B1,
        ... )
        True
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.Corridor2, DeepPositionNameEnum.B4,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.Corridor2, DeepPositionNameEnum.A1,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.Corridor2, DeepPositionNameEnum.A2,
        ... )
        False
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A3: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A4: AmphipodEnum.B,
        ...     DeepPositionNameEnum.Corridor2: AmphipodEnum.A,
        ... })
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A1, DeepPositionNameEnum.Corridor3,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A2, DeepPositionNameEnum.Corridor3,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A3, DeepPositionNameEnum.Corridor3,
        ... )
        False
        >>> maze.can_move_to(
        ...     DeepPositionNameEnum.A4, DeepPositionNameEnum.Corridor3,
        ... )
        True
        """
        return not self.why_cant_move_to(start, end)

    # noinspection DuplicatedCode
    def why_cant_move_to(
        self, start: DeepPositionNameEnum, end: DeepPositionNameEnum,
    ) -> Optional[str]:
        if start.is_corridor and end.is_corridor:
            return "Both are in the corridor"
        if end in self.amphipod_map:
            return "End is filled"
        if start not in self.amphipod_map:
            return "Start is empty"

        if not start.is_corridor and not end.is_corridor:
            if self.is_position_name_finished(start):
                return "Start room is finished"
            if self.is_position_name_finished(end):
                return "End room is finished"
        else:
            if start.is_corridor:
                corridor, room = start, end
            else:
                corridor, room = end, start
            if self.is_position_name_finished(room):
                return "Room is finished"
        if not end.is_corridor:
            if self.amphipod_map[start] != end.amphipod:
                return "Amphipod of start doesn't match end room amphipod"
            if not end.is_inner:
                if not all(
                    self.is_position_name_finished(inner)
                    for inner in end.inner_ones
                ):
                    return "Some inner rooms of end is not finished"
        position_names_between = start.get_position_names_between(end)
        for position_name in position_names_between:
            if position_name in self.amphipod_map:
                return "There is an obstacle in the way"

        return None

    def is_position_name_finished(
        self, position_name: DeepPositionNameEnum,
    ) -> bool:
        """
        >>> maze = DeepMaze({})
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A1)
        False
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A2)
        False
        >>> maze.is_position_name_finished(DeepPositionNameEnum.Corridor1)
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ... })
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A1)
        True
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A2)
        False
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... })
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A1)
        False
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A2)
        False
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... })
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A1)
        True
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A2)
        True
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.B,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.A,
        ... })
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A1)
        False
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A2)
        False
        >>> maze = DeepMaze({
        ...     DeepPositionNameEnum.A1: AmphipodEnum.A,
        ...     DeepPositionNameEnum.A2: AmphipodEnum.B,
        ... })
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A1)
        True
        >>> maze.is_position_name_finished(DeepPositionNameEnum.A2)
        False
        """
        amphipod = position_name.amphipod
        if position_name not in self.amphipod_map:
            return False
        amphipod_at_position = self.amphipod_map[position_name]
        if amphipod != amphipod_at_position:
            return False
        if position_name.is_inner:
            return True

        return all(
            self.is_position_name_finished(inner)
            for inner in position_name.inner_ones
        )


Challenge.main()
challenge = Challenge()
