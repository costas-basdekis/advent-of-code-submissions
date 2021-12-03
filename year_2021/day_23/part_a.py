#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum

import math
from itertools import combinations
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, iterable_length


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        15365
        """
        return Maze\
            .from_maze_text(_input)\
            .find_minimum_cost_to_organise(debugger=debugger)


class AmphipodEnum(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

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

    def __lt__(self, other: "AmphipodEnum") -> bool:
        return self.value < other.value

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    MOVE_COST_MAP: Dict["AmphipodEnum", int]

    @property
    def move_cost(self) -> int:
        return self.MOVE_COST_MAP[self]


AmphipodEnum.MOVE_COST_MAP = {
    AmphipodEnum.A: 1,
    AmphipodEnum.B: 10,
    AmphipodEnum.C: 100,
    AmphipodEnum.D: 1000,
}


class PositionNameEnum(Enum):
    Corridor1 = "1"
    Corridor2 = "2"
    Corridor3 = "3"
    Corridor4 = "4"
    Corridor5 = "5"
    Corridor6 = "6"
    Corridor7 = "7"
    AInner = "A"
    AOuter = "a"
    BInner = "B"
    BOuter = "b"
    CInner = "C"
    COuter = "c"
    DInner = "D"
    DOuter = "d"

    @classmethod
    def from_position(cls, position: Point2D) -> "PositionNameEnum":
        """
        >>> PositionNameEnum.from_position(Point2D(x=1, y=1))
        PositionNameEnum.Corridor1
        >>> PositionNameEnum.from_position(Point2D(x=2, y=1))
        PositionNameEnum.Corridor2
        >>> PositionNameEnum.from_position(Point2D(x=3, y=3))
        PositionNameEnum.AInner
        >>> PositionNameEnum.from_position(Point2D(x=3, y=2))
        PositionNameEnum.AOuter
        """
        position_name = cls.maybe_from_position(position)
        if not position_name:
            raise Exception(f"No position name for {position}")
        return position_name

    @classmethod
    def maybe_from_position(
        cls, position: Point2D,
    ) -> Optional["PositionNameEnum"]:
        """
        >>> PositionNameEnum.maybe_from_position(Point2D(x=1, y=1))
        PositionNameEnum.Corridor1
        >>> PositionNameEnum.maybe_from_position(Point2D(x=2, y=1))
        PositionNameEnum.Corridor2
        >>> PositionNameEnum.maybe_from_position(Point2D(x=3, y=3))
        PositionNameEnum.AInner
        >>> PositionNameEnum.maybe_from_position(Point2D(x=3, y=2))
        PositionNameEnum.AOuter
        >>> PositionNameEnum.maybe_from_position(Point2D(x=0, y=0))
        """
        try:
            return cls(cls.MAZE_LINES[position.y][position.x])
        except ValueError:
            return None

    @classmethod
    def get_rooms(cls) -> Set["PositionNameEnum"]:
        """
        >>> sorted(PositionNameEnum.get_rooms())
        [PositionNameEnum.AInner, PositionNameEnum.AOuter,
            PositionNameEnum.BInner, PositionNameEnum.BOuter,
            PositionNameEnum.CInner, PositionNameEnum.COuter,
            PositionNameEnum.DInner, PositionNameEnum.DOuter]
        """
        return {
            position
            for position in cls
            if not position.is_corridor
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __lt__(self, other: "PositionNameEnum") -> bool:
        if self.value.lower() == other.value.lower():
            return self.value < other.value
        else:
            return self.value.lower() < other.value.lower()

    MAZE_LINES: List[str]

    @property
    def position(self) -> Point2D:
        """
        >>> PositionNameEnum.Corridor1.position
        Point2D(x=1, y=1)
        >>> PositionNameEnum.Corridor2.position
        Point2D(x=2, y=1)
        >>> PositionNameEnum.AInner.position
        Point2D(x=3, y=3)
        >>> PositionNameEnum.AOuter.position
        Point2D(x=3, y=2)
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

    def get_distance_to(self, other: "PositionNameEnum") -> int:
        """
        >>> PositionNameEnum.AInner.get_distance_to(PositionNameEnum.Corridor1)
        4
        >>> PositionNameEnum.AInner.get_distance_to(PositionNameEnum.BInner)
        6
        >>> PositionNameEnum.AInner.get_distance_to(PositionNameEnum.BOuter)
        5
        >>> PositionNameEnum.AInner.get_distance_to(PositionNameEnum.AOuter)
        1
        >>> PositionNameEnum.AInner.get_distance_to(PositionNameEnum.AInner)
        0
        """
        if self.is_corridor and other.is_corridor:
            raise ValueError(
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

    @property
    def is_corridor(self) -> bool:
        """
        >>> PositionNameEnum.AInner.is_corridor
        False
        >>> PositionNameEnum.Corridor1.is_corridor
        True
        """
        return "Corridor" in self.name

    @property
    def is_inner(self) -> bool:
        """
        >>> PositionNameEnum.AInner.is_inner
        True
        >>> PositionNameEnum.AOuter.is_inner
        False
        >>> PositionNameEnum.Corridor1.is_inner
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if self.is_corridor:
            raise ValueError(f"{self} is a corridor")
        return "Inner" in self.name

    @property
    def inner(self) -> "PositionNameEnum":
        """
        >>> PositionNameEnum.AInner.inner
        PositionNameEnum.AInner
        >>> PositionNameEnum.AOuter.inner
        PositionNameEnum.AInner
        >>> PositionNameEnum.Corridor1.inner
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if self.is_inner:
            return self

        return type(self)(self.value.upper())

    @property
    def outer(self) -> "PositionNameEnum":
        """
        >>> PositionNameEnum.AInner.outer
        PositionNameEnum.AOuter
        >>> PositionNameEnum.AOuter.outer
        PositionNameEnum.AOuter
        >>> PositionNameEnum.Corridor1.outer
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if not self.is_inner:
            return self

        return type(self)(self.value.lower())

    @property
    def amphipod(self) -> AmphipodEnum:
        """
        >>> PositionNameEnum.AInner.amphipod
        AmphipodEnum.A
        >>> PositionNameEnum.AOuter.amphipod
        AmphipodEnum.A
        >>> PositionNameEnum.Corridor1.amphipod
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        return AmphipodEnum(self.inner.value)

    def get_position_names_between(
        self, other: "PositionNameEnum",
    ) -> List["PositionNameEnum"]:
        """
        >>> PositionNameEnum.AInner\\
        ...     .get_position_names_between(PositionNameEnum.Corridor1)
        [PositionNameEnum.AOuter, PositionNameEnum.Corridor1,
            PositionNameEnum.Corridor2]
        >>> PositionNameEnum.AOuter\\
        ...     .get_position_names_between(PositionNameEnum.Corridor1)
        [PositionNameEnum.Corridor1, PositionNameEnum.Corridor2]
        >>> PositionNameEnum.AInner\\
        ...     .get_position_names_between(PositionNameEnum.Corridor5)
        [PositionNameEnum.AOuter, PositionNameEnum.Corridor3,
            PositionNameEnum.Corridor4, PositionNameEnum.Corridor5]
        >>> PositionNameEnum.COuter\\
        ...     .get_position_names_between(PositionNameEnum.Corridor2)
        [PositionNameEnum.Corridor2,
            PositionNameEnum.Corridor3, PositionNameEnum.Corridor4]
        >>> PositionNameEnum.Corridor1\\
        ...     .get_position_names_between(PositionNameEnum.AInner)
        [PositionNameEnum.AInner, PositionNameEnum.AOuter,
            PositionNameEnum.Corridor2]
        >>> PositionNameEnum.Corridor1\\
        ...     .get_position_names_between(PositionNameEnum.AOuter)
        [PositionNameEnum.AOuter, PositionNameEnum.Corridor2]
        >>> PositionNameEnum.Corridor5\\
        ...     .get_position_names_between(PositionNameEnum.AInner)
        [PositionNameEnum.AInner, PositionNameEnum.AOuter,
            PositionNameEnum.Corridor3, PositionNameEnum.Corridor4]
        >>> PositionNameEnum.Corridor2\\
        ...     .get_position_names_between(PositionNameEnum.COuter)
        [PositionNameEnum.COuter, PositionNameEnum.Corridor3,
            PositionNameEnum.Corridor4]
        >>> PositionNameEnum.AInner\\
        ...     .get_position_names_between(PositionNameEnum.AOuter)
        [PositionNameEnum.AOuter]
        """
        if self.is_corridor and other.is_corridor:
            raise ValueError(
                "Cannot get position names between two on the corridor "
                "({self} and {other})"
            )

        cls = type(self)
        if not self.is_corridor and not other.is_corridor:
            if self.position.x == other.position.x:
                return [other]
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
        if room.is_inner:
            position_names_between.append(room.outer)

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

    ROOM_NUMBER_MAP: Dict["PositionNameEnum", float]

    @property
    def room_number(self) -> float:
        """
        >>> PositionNameEnum.AInner.room_number
        2.5
        >>> PositionNameEnum.AOuter.room_number
        2.5
        >>> PositionNameEnum.DInner.room_number
        5.5
        >>> PositionNameEnum.DOuter.room_number
        5.5
        >>> PositionNameEnum.Corridor1.room_number
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if self.is_corridor:
            raise ValueError(f"{self} is not a room")
        return self.ROOM_NUMBER_MAP[self]

    @property
    def corridor_number(self) -> int:
        """
        >>> PositionNameEnum.Corridor1.corridor_number
        1
        >>> PositionNameEnum.Corridor5.corridor_number
        5
        >>> PositionNameEnum.AInner.corridor_number
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if not self.is_corridor:
            raise ValueError(
                f"Cannot get corridor number of non-corridor ({self})"
            )

        return int(self.value)


PositionNameEnum.MAZE_LINES = list(filter(None, """
    #############
    #12.3.4.5.67#
    ###a#b#c#d###
    ..#A#B#C#D#..
    ..#########..
""".replace(" ", "").splitlines()))

PositionNameEnum.ROOM_NUMBER_MAP = {
    PositionNameEnum.AInner: 2.5,
    PositionNameEnum.AOuter: 2.5,
    PositionNameEnum.BInner: 3.5,
    PositionNameEnum.BOuter: 3.5,
    PositionNameEnum.CInner: 4.5,
    PositionNameEnum.COuter: 4.5,
    PositionNameEnum.DInner: 5.5,
    PositionNameEnum.DOuter: 5.5,
}


@dataclass
class Maze:
    amphipod_map: Dict[PositionNameEnum, AmphipodEnum]

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
        >>> len(maze.amphipod_map)
        8
        >>> print(maze)
        #############
        #...........#
        ###A#D#C#A###
        ..#C#D#B#B#..
        ..#########..
        """
        lines = cls.trim_maze(maze_text)
        return cls(
            amphipod_map={
                position_name: AmphipodEnum(lines[position.y][position.x])
                for position_name in PositionNameEnum.get_rooms()
                for position in [position_name.position]
            },
        )

    @classmethod
    def trim_maze(cls, maze_text: str) -> List[str]:
        """
        >>> print("\\n".join(Maze.trim_maze('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''')))
        #############
        #...........#
        ###A#D#C#A###
          #C#D#B#B#
          #########
        """
        lines = [
            line.rstrip()
            for line in maze_text.splitlines()
            if line.strip()
        ]
        prefix_length = len(lines[0]) - len(lines[0].lstrip())
        return [
            line[prefix_length:]
            for line in lines
        ]

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
                in [PositionNameEnum.maybe_from_position(position)]
            )
            for y, line in enumerate(PositionNameEnum.MAZE_LINES)
        )

    def __hash__(self) -> int:
        """
        >>> maze_a = Maze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''')
        >>> maze_b = Maze.from_maze_text('''
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
        >>> Maze({}).finished
        True
        >>> Maze({
        ...     PositionNameEnum.Corridor1: AmphipodEnum.A,
        ... }).finished
        False
        >>> Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ... }).finished
        True
        >>> Maze({
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... }).finished
        False
        >>> Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ...     PositionNameEnum.Corridor1: AmphipodEnum.A,
        ... }).finished
        False
        >>> Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ...     PositionNameEnum.AOuter: AmphipodEnum.B,
        ... }).finished
        False
        >>> Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.B,
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... }).finished
        False
        >>> Maze({
        ...     PositionNameEnum.BInner: AmphipodEnum.B,
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... }).finished
        False
        >>> Maze({
        ...     PositionNameEnum.BInner: AmphipodEnum.B,
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
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
        >>> Maze({}).finish_count
        0
        >>> Maze({
        ...     PositionNameEnum.Corridor1: AmphipodEnum.A,
        ... }).finish_count
        0
        >>> Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ... }).finish_count
        1
        >>> Maze({
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... }).finish_count
        0
        >>> Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ...     PositionNameEnum.Corridor1: AmphipodEnum.A,
        ... }).finish_count
        1
        >>> Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ...     PositionNameEnum.AOuter: AmphipodEnum.B,
        ... }).finish_count
        1
        >>> Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.B,
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... }).finish_count
        0
        >>> Maze({
        ...     PositionNameEnum.BInner: AmphipodEnum.B,
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... }).finish_count
        1
        >>> Maze({
        ...     PositionNameEnum.BInner: AmphipodEnum.B,
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ... }).finish_count
        2
        """
        return iterable_length(filter(None, (
            not position_name.is_corridor
            and self.is_position_name_finished(position_name)
            for position_name in self.amphipod_map
        )))

    def find_minimum_cost_to_organise(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> Maze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###B#C#B#D###
        ...       #A#D#C#A#
        ...       #########
        ... ''').find_minimum_cost_to_organise()
        12521
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

    def get_next_moves(self) -> Iterable[Tuple[int, "Maze"]]:
        for start, end in self.get_next_trips():
            yield self.get_cost_for(start, end), self.move(start, end)

    def get_next_trips(
        self,
    ) -> Iterable[Tuple[PositionNameEnum, PositionNameEnum]]:
        """
        >>> list(Maze({}).get_next_trips())
        []
        """
        for first, second in combinations(PositionNameEnum, 2):
            if self.can_move_to(first, second):
                yield first, second
            elif self.can_move_to(second, first):
                yield second, first

    def get_cost_for(
        self, start: PositionNameEnum, end: PositionNameEnum,
    ) -> int:
        return start.get_distance_to(end) * self.amphipod_map[start].move_cost

    def move(self, start: PositionNameEnum, end: PositionNameEnum) -> "Maze":
        """
        >>> print(Maze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''').move(PositionNameEnum.AOuter, PositionNameEnum.Corridor1))
        #############
        #A..........#
        ###.#D#C#A###
        ..#C#D#B#B#..
        ..#########..
        >>> print(Maze.from_maze_text('''
        ...     #############
        ...     #...........#
        ...     ###A#D#C#A###
        ...       #C#D#B#B#
        ...       #########
        ... ''').move(PositionNameEnum.BOuter, PositionNameEnum.Corridor7))
        #############
        #..........D#
        ###A#.#C#A###
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
        self, start: PositionNameEnum, end: PositionNameEnum,
    ) -> bool:
        """
        >>> maze = Maze({})
        >>> maze.can_move_to(
        ...     PositionNameEnum.AInner, PositionNameEnum.Corridor1,
        ... )
        False
        >>> maze = Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ... })
        >>> maze.can_move_to(
        ...     PositionNameEnum.AInner, PositionNameEnum.Corridor1,
        ... )
        False
        >>> maze = Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.B,
        ... })
        >>> maze.can_move_to(
        ...     PositionNameEnum.AInner, PositionNameEnum.Corridor1,
        ... )
        True
        >>> maze = Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.B,
        ...     PositionNameEnum.AOuter: AmphipodEnum.B,
        ... })
        >>> maze.can_move_to(
        ...     PositionNameEnum.AOuter, PositionNameEnum.Corridor1,
        ... )
        True
        >>> maze.can_move_to(
        ...     PositionNameEnum.AInner, PositionNameEnum.Corridor1,
        ... )
        False
        >>> maze = Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.B,
        ...     PositionNameEnum.AOuter: AmphipodEnum.B,
        ...     PositionNameEnum.Corridor2: AmphipodEnum.A,
        ... })
        >>> maze.can_move_to(
        ...     PositionNameEnum.AOuter, PositionNameEnum.Corridor1,
        ... )
        False
        >>> maze.can_move_to(
        ...     PositionNameEnum.AOuter, PositionNameEnum.Corridor2,
        ... )
        False
        >>> maze.can_move_to(
        ...     PositionNameEnum.AOuter, PositionNameEnum.Corridor3,
        ... )
        True
        >>> maze.can_move_to(
        ...     PositionNameEnum.AOuter, PositionNameEnum.BInner,
        ... )
        True
        >>> maze.can_move_to(
        ...     PositionNameEnum.AOuter, PositionNameEnum.BOuter,
        ... )
        False
        >>> maze.can_move_to(
        ...     PositionNameEnum.AOuter, PositionNameEnum.CInner,
        ... )
        False
        >>> maze.can_move_to(
        ...     PositionNameEnum.AOuter, PositionNameEnum.COuter,
        ... )
        False
        >>> maze = Maze({
        ...     PositionNameEnum.Corridor2: AmphipodEnum.B,
        ... })
        >>> maze.can_move_to(
        ...     PositionNameEnum.Corridor2, PositionNameEnum.BInner,
        ... )
        True
        >>> maze.can_move_to(
        ...     PositionNameEnum.Corridor2, PositionNameEnum.BOuter,
        ... )
        False
        >>> maze.can_move_to(
        ...     PositionNameEnum.Corridor2, PositionNameEnum.AInner,
        ... )
        False
        >>> maze.can_move_to(
        ...     PositionNameEnum.Corridor2, PositionNameEnum.AOuter,
        ... )
        False
        """
        return not self.why_cant_move_to(start, end)

    def why_cant_move_to(
        self, start: PositionNameEnum, end: PositionNameEnum,
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
                if not self.is_position_name_finished(end.inner):
                    return "Inner room of end is not finished"
        position_names_between = start.get_position_names_between(end)
        for position_name in position_names_between:
            if position_name in self.amphipod_map:
                return "There is an obstacle in the way"

        return None

    def is_position_name_finished(
        self, position_name: PositionNameEnum,
    ) -> bool:
        """
        >>> maze = Maze({})
        >>> maze.is_position_name_finished(PositionNameEnum.AInner)
        False
        >>> maze.is_position_name_finished(PositionNameEnum.AOuter)
        False
        >>> maze.is_position_name_finished(PositionNameEnum.Corridor1)
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> maze = Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ... })
        >>> maze.is_position_name_finished(PositionNameEnum.AInner)
        True
        >>> maze.is_position_name_finished(PositionNameEnum.AOuter)
        False
        >>> maze = Maze({
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... })
        >>> maze.is_position_name_finished(PositionNameEnum.AInner)
        False
        >>> maze.is_position_name_finished(PositionNameEnum.AOuter)
        False
        >>> maze = Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... })
        >>> maze.is_position_name_finished(PositionNameEnum.AInner)
        True
        >>> maze.is_position_name_finished(PositionNameEnum.AOuter)
        True
        >>> maze = Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.B,
        ...     PositionNameEnum.AOuter: AmphipodEnum.A,
        ... })
        >>> maze.is_position_name_finished(PositionNameEnum.AInner)
        False
        >>> maze.is_position_name_finished(PositionNameEnum.AOuter)
        False
        >>> maze = Maze({
        ...     PositionNameEnum.AInner: AmphipodEnum.A,
        ...     PositionNameEnum.AOuter: AmphipodEnum.B,
        ... })
        >>> maze.is_position_name_finished(PositionNameEnum.AInner)
        True
        >>> maze.is_position_name_finished(PositionNameEnum.AOuter)
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

        return self.is_position_name_finished(position_name.inner)


Challenge.main()
challenge = Challenge()
