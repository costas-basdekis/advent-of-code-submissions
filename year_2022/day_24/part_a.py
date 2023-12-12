#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
from itertools import groupby
from typing import ClassVar, Dict, Iterable, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        373
        """
        return Valley.from_valley_map(_input).get_min_steps_to_exit(debugger=debugger)


class Direction(Enum):
    North = "north"
    South = "south"
    West = "west"
    East = "east"

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __lt__(self, other: "Direction") -> bool:
        directions = list(Direction)
        return directions.index(self) < directions.index(other)


@dataclass(eq=True, frozen=True, order=True)
class Valley:
    walls: Set[Point2D]
    blizzards_by_position: Dict[Point2D, List["Blizzard"]]
    width: int
    height: int
    position: Point2D

    @classmethod
    def from_valley_map(cls, text: str) -> "Valley":
        """
        >>> print(Valley.from_valley_map('''
        ... #.#####
        ... #.....#
        ... #>....#
        ... #.....#
        ... #...v.#
        ... #.....#
        ... #####.#
        ... '''))
        #E#####
        #.....#
        #>....#
        #.....#
        #...v.#
        #.....#
        #####.#
        >>> print(Valley.from_valley_map('''
        ... #E######
        ... #>>.<^<#
        ... #.<..<<#
        ... #>v.><>#
        ... #<^v^^>#
        ... ######.#
        ... '''))
        #E######
        #>>.<^<#
        #.<..<<#
        #>v.><>#
        #<^v^^>#
        ######.#
        """
        lines = list(map(str.strip, text.strip().split("\n")))
        walls = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char == "#"
        }
        blizzards: Iterable["Blizzard"] = [
            Blizzard.from_position_and_char(position, char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            for position in [Point2D(x, y)]
            if char in Blizzard.DIRECTION_PARSE_MAP
        ]
        blizzards_by_position = cls.group_blizzards(blizzards)
        _, (max_x, max_y) = min_and_max_tuples(walls)
        positions = [
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char == "E"
        ]
        if len(positions) > 1:
            raise Exception(f"Too many positions: {positions}")
        if positions:
            position, = positions
        else:
            position = Point2D(1, 0)
        empty_spots = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char == "."
        }
        non_empty_spots = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
        } - empty_spots - walls - {blizzard.position for blizzard in blizzards} - set(positions)
        if non_empty_spots:
            non_empty_values = {
                char
                for y, line in enumerate(lines)
                for x, char in enumerate(line)
                if Point2D(x, y) in non_empty_spots
            }
            raise Exception(f"There were non-empty spots: {non_empty_spots} with values {non_empty_values}")
        return cls(
            walls=walls,
            blizzards_by_position=blizzards_by_position,
            width=max_x + 1, height=max_y + 1,
            position=position,
        )

    @classmethod
    def group_blizzards(cls, blizzards: Iterable["Blizzard"]) -> Dict[Point2D, List["Blizzard"]]:
        """
        >>> Valley.group_blizzards([
        ...     Blizzard(Point2D(3, 1), Direction.West),
        ...     Blizzard(Point2D(4, 1), Direction.West),
        ...     Blizzard(Point2D(3, 1), Direction.South),
        ...     Blizzard(Point2D(3, 1), Direction.East),
        ... ])
        {Point2D(x=3, y=1): [Blizzard(position=Point2D(x=3, y=1), direction=Direction.West),
            Blizzard(position=Point2D(x=3, y=1), direction=Direction.South),
            Blizzard(position=Point2D(x=3, y=1), direction=Direction.East)],
            Point2D(x=4, y=1): [Blizzard(position=Point2D(x=4, y=1), direction=Direction.West)]}
        >>> _valley = Valley.from_valley_map('''
        ... #E######
        ... #>>.<^<#
        ... #.<..<<#
        ... #>v.><>#
        ... #<^v^^>#
        ... ######.#
        ... ''')
        """
        return {
            position: list(blizzard_group)
            for position, blizzard_group
            in groupby(sorted(blizzards, key=lambda blizzard: blizzard.position), lambda blizzard: blizzard.position)
        }

    def get_min_steps_to_exit(self, target: Optional[Point2D] = None, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> _valley = Valley.from_valley_map('''
        ... #E######
        ... #>>.<^<#
        ... #.<..<<#
        ... #>v.><>#
        ... #<^v^^>#
        ... ######.#
        ... ''')
        >>> _valley.get_min_steps_to_exit()
        18
        """
        path, _ = self.find_shortest_exit_path(target, debugger)
        return len(path)

    def find_shortest_exit_path(self, target: Optional[Point2D] = None, debugger: Debugger = Debugger(enabled=False)) -> Tuple[List[Optional[Direction]], "Valley"]:
        """
        >>> _valley = Valley.from_valley_map('''
        ... #E######
        ... #>>.<^<#
        ... #.<..<<#
        ... #>v.><>#
        ... #<^v^^>#
        ... ######.#
        ... ''')
        >>> _path, end_valley = _valley.find_shortest_exit_path()
        >>> print(end_valley)
        #.######
        #>2.<.<#
        #.2v^2<#
        #>..>2>#
        #<....>#
        ######E#
        >>> print(_valley.make_moves(_path))
        #.######
        #>2.<.<#
        #.2v^2<#
        #>..>2>#
        #<....>#
        ######E#
        """
        if target is None:
            target = Point2D(self.width -  2, self.height - 1)
        queue: List[Tuple[List[Optional[Direction]], Valley]] = [([], self)]
        seen_by_step_count: Dict[int, Set[Point2D]] = {0: {self.position}}
        just_blizzards_cache: Dict[int, Valley] = {}
        while debugger.step_if(queue):
            path, valley = queue.pop(0)
            step_count = len(path)
            if step_count not in just_blizzards_cache:
                just_blizzards_cache[step_count] = valley.step_blizzards()
            for direction, next_valley in valley.get_next_moves(just_blizzards=just_blizzards_cache[step_count]):
                next_path = path + [direction]
                if next_valley.position == target:
                    return next_path, next_valley
                seen = seen_by_step_count.setdefault(len(next_path), set())
                if next_valley.position in seen:
                    continue
                seen.add(next_valley.position)
                queue.append((next_path, next_valley))
            if debugger.should_report():
                debugger.default_report_if(
                    f"Seen {sum(map(len, seen_by_step_count.values()))} valleys, "
                    f"{len(queue)} remaining, "
                    f"{step_count} current path length",
                )
        raise Exception("Could not find exit")

    def get_next_moves(self, just_blizzards: Optional["Valley"]=None) -> Iterable[Tuple[Optional[Direction], "Valley"]]:
        """
        >>> _valley = Valley.from_valley_map('''
        ... #E######
        ... #>>.<^<#
        ... #.<..<<#
        ... #>v.><>#
        ... #<^v^^>#
        ... ######.#
        ... ''')
        >>> print("\\n".join(str(next_valley) for _, next_valley in _valley.get_next_moves()))
        #E######
        #.>3.<.#
        #<..<<.#
        #>2.22.#
        #>v..^<#
        ######.#
        #.######
        #E>3.<.#
        #<..<<.#
        #>2.22.#
        #>v..^<#
        ######.#
        """
        if not just_blizzards:
            just_blizzards = self.step_blizzards()
        if self.position not in just_blizzards.blizzards_by_position:
            yield None, just_blizzards.move_to(self.position)
        for direction in Direction:
            position = self.position.offset(Blizzard.OFFSET_BY_DIRECTION[direction])
            if not just_blizzards.can_move_to(position):
                continue
            yield direction, just_blizzards.move_to(position)

    def position_is_within_bounds(self, position: Point2D) -> bool:
        return 0 <= position.x < self.width and 0 <= position.y < self.height

    def make_moves(self, directions: List[Optional[Direction]]) -> "Valley":
        """
        >>> _valley = Valley.from_valley_map('''
        ... #E######
        ... #>>.<^<#
        ... #.<..<<#
        ... #>v.><>#
        ... #<^v^^>#
        ... ######.#
        ... ''')
        >>> _directions = [
        ...     Direction.South,
        ...     Direction.South,
        ...     None,
        ...     Direction.North,
        ...     Direction.East,
        ...     Direction.East,
        ...     Direction.South,
        ...     Direction.West,
        ...     Direction.North,
        ...     Direction.East,
        ...     None,
        ...     Direction.South,
        ...     Direction.South,
        ...     Direction.East,
        ...     Direction.East,
        ...     Direction.East,
        ...     Direction.South,
        ...     Direction.South,
        ... ]
        >>> print(_valley.make_moves(_directions))
        #.######
        #>2.<.<#
        #.2v^2<#
        #>..>2>#
        #<....>#
        ######E#
        """
        valley = self
        for direction in directions:
            valley = valley.step_blizzards()
            if not direction:
                valley = valley.move_to(valley.position)
                continue
            valley = valley.move_to(valley.position.offset(Blizzard.OFFSET_BY_DIRECTION[direction]))
        return valley

    def can_move_to(self, position: Point2D) -> bool:
        if position in self.walls:
            return False
        if position in self.blizzards_by_position:
            return False
        if not self.position_is_within_bounds(position):
            return False
        return True

    def move_to(self, position: Point2D) -> "Valley":
        if position == self.position:
            return self
        cls = type(self)
        if position in self.walls:
            raise Exception(f"Position {position} hits a wall")
        if position in self.blizzards_by_position:
            raise Exception(f"Position {position} hits a blizzard")
        return cls(
            walls=self.walls,
            blizzards_by_position=self.blizzards_by_position,
            width=self.width, height=self.height,
            position=position,
        )

    def step_blizzards_many(self, count: int) -> "Valley":
        """
        >>> _valley = Valley.from_valley_map('''
        ... #.#####
        ... #.....#
        ... #>....#
        ... #.....#
        ... #...v.#
        ... #.....#
        ... #####.#
        ... ''')
        >>> print(_valley.step_blizzards_many(1))
        #E#####
        #.....#
        #.>...#
        #.....#
        #.....#
        #...v.#
        #####.#
        >>> print(_valley.step_blizzards_many(2))
        #E#####
        #...v.#
        #..>..#
        #.....#
        #.....#
        #.....#
        #####.#
        >>> print(_valley.step_blizzards_many(3))
        #E#####
        #.....#
        #...2.#
        #.....#
        #.....#
        #.....#
        #####.#
        >>> print(_valley.step_blizzards_many(4))
        #E#####
        #.....#
        #....>#
        #...v.#
        #.....#
        #.....#
        #####.#
        >>> print(_valley.step_blizzards_many(5))
        #E#####
        #.....#
        #>....#
        #.....#
        #...v.#
        #.....#
        #####.#
        """
        valley = self
        for _ in range(count):
            valley = valley.step_blizzards()
        return valley

    def step_blizzards(self) -> "Valley":
        """
        >>> print(Valley.from_valley_map('''
        ... #.#####
        ... #.....#
        ... #>....#
        ... #.....#
        ... #...v.#
        ... #.....#
        ... #####.#
        ... ''').step_blizzards())
        #E#####
        #.....#
        #.>...#
        #.....#
        #.....#
        #...v.#
        #####.#
        >>> _valley = Valley.from_valley_map('''
        ... #E######
        ... #>>.<^<#
        ... #.<..<<#
        ... #>v.><>#
        ... #<^v^^>#
        ... ######.#
        ... ''')
        >>> print(_valley.step_blizzards())
        #E######
        #.>3.<.#
        #<..<<.#
        #>2.22.#
        #>v..^<#
        ######.#
        >>> len(_valley.step_blizzards().blizzards_by_position[Point2D(3, 1)])
        3
        """
        blizzards = (
            self.step_blizzard(blizzard)
            for blizzards in self.blizzards_by_position.values()
            for blizzard in blizzards
        )
        blizzards_by_position = self.group_blizzards(blizzards)
        cls = type(self)
        return cls(
            walls=self.walls,
            blizzards_by_position=blizzards_by_position,
            width=self.width, height=self.height,
            position=self.position,
        )

    def step_blizzard(self, blizzard: "Blizzard") -> "Blizzard":
        return blizzard.move_to(self.get_blizzard_new_position(blizzard))

    def get_blizzard_new_position(self, blizzard: "Blizzard") -> Point2D:
        offset = blizzard.direction_offset
        next_position: Point2D = blizzard.position.offset(offset)
        if next_position in self.walls:
            if blizzard.direction == Direction.North:
                next_position = next_position.replace_dimension(1, self.height - 2)
            elif blizzard.direction == Direction.South:
                next_position = next_position.replace_dimension(1, 1)
            elif blizzard.direction == Direction.West:
                next_position = next_position.replace_dimension(0, self.width - 2)
            elif blizzard.direction == Direction.East:
                next_position = next_position.replace_dimension(0, 1)
            else:
                raise Exception(f"Unknown direction {blizzard.direction}")
        return next_position

    def __str__(self) -> str:
        return "\n".join(
            "".join(
                str(blizzards[0])
                if blizzards and (len(blizzards) == 1) else
                str(len(blizzards))
                if blizzards else
                "#"
                if point in self.walls else
                "E"
                if self.position == point else
                "."
                for x in range(self.width)
                for point in [Point2D(x, y)]
                for blizzards in [self.blizzards_by_position.get(point)]
            )
            for y in range(self.height)
        )


@dataclass(frozen=True, eq=True, order=True)
class Blizzard:
    position: Point2D
    direction: Direction

    DIRECTION_MAP: ClassVar[Dict[Direction, str]] = {
        Direction.North: "^",
        Direction.South: "v",
        Direction.West: "<",
        Direction.East: ">",
    }
    DIRECTION_PARSE_MAP: ClassVar[Dict[str, Direction]] = {
        char: direction
        for direction, char in DIRECTION_MAP.items()
    }
    OFFSET_BY_DIRECTION: ClassVar[Dict[Direction, Point2D]] = {
        Direction.North: (0, -1),
        Direction.South: (0, 1),
        Direction.West: (-1, 0),
        Direction.East: (1, 0),
    }

    @classmethod
    def from_position_and_char(cls, position: Point2D, char: str) -> "Blizzard":
        return cls(position=position, direction=cls.DIRECTION_PARSE_MAP[char])

    def __str__(self) -> str:
        return self.DIRECTION_MAP[self.direction]

    def move_to(self, position: Point2D) -> "Blizzard":
        cls = type(self)
        return cls(position=position, direction=self.direction)

    @property
    def direction_offset(self) -> Point2D:
        return self.OFFSET_BY_DIRECTION[self.direction]


Challenge.main()
challenge = Challenge()
