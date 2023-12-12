#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import ClassVar, Dict, Iterable, List, Optional, Set, Tuple, Union, Generic, TypeVar, Type

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Cls, Self, Direction, min_and_max_tuples, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        40714
        """
        return DigInstructionSet.from_instructions_text(_input).dig().extend_with_internal().hole_count


@dataclass
class Lagoon:
    holes: Set[Point2D]

    @classmethod
    def empty(cls: Cls["Lagoon"]) -> Self["Lagoon"]:
        return cls(holes=set())

    def __str__(self) -> str:
        if not self.holes:
            return ""
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.holes)
        return "\n".join(
            "".join(
                "#"
                if Point2D(x, y) in self.holes else
                "."
                for x in range(min_x, max_x + 1)
            )
            for y in range(min_y, max_y + 1)
        )

    def add(self: Self["Lagoon"], position: Point2D) -> Self["Lagoon"]:
        self.holes.add(position)
        return self

    def extend(self: Self["Lagoon"], positions: Iterable[Point2D]) -> Self["Lagoon"]:
        self.holes.update(positions)
        return self

    def extend_with_internal(self, debugger: Debugger = Debugger(enabled=False)) -> "Lagoon":
        """
        >>> print(DigInstructionSet.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').dig().extend_with_internal())
        #######
        #######
        #######
        ..#####
        ..#####
        #######
        #####..
        #######
        .######
        .######
        """
        return self.extend(LagoonFiller.from_lagoon(self).get_enclosed_positions(debugger=debugger))

    @property
    def hole_count(self) -> int:
        """
        >>> lagoon = DigInstructionSet.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').dig()
        >>> lagoon.hole_count
        38
        >>> lagoon.extend_with_internal().hole_count
        62
        """
        return len(self.holes)


@dataclass
class LagoonFiller:
    lagoon: Lagoon
    inside: Set[Point2D]
    outside: Set[Point2D]
    boundaries: Tuple[Point2D, Point2D]

    @classmethod
    def from_lagoon(cls, lagoon: Lagoon) -> "LagoonFiller":
        return cls(
            lagoon=lagoon,
            inside=set(),
            outside=set(),
            boundaries=min_and_max_tuples(lagoon.holes),
        )

    def get_enclosed_positions(self, debugger: Debugger = Debugger(enabled=False)) -> Set[Point2D]:
        """
        >>> len(LagoonFiller.from_lagoon(DigInstructionSet.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').dig()).get_enclosed_positions())
        24
        """
        for position in debugger.stepping(self.lagoon.holes):
            for neighbour in position.get_euclidean_neighbours():
                self.flood(neighbour)
            if debugger.should_report():
                debugger.default_report_if(f"Found {len(self.inside)} inside points and {len(self.outside)} outside points")
        return self.inside

    def flood(self, start: Point2D) -> "LagoonFiller":
        """
        >>> _lagoon = DigInstructionSet.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').dig()
        >>> _filler = LagoonFiller.from_lagoon(_lagoon).flood(Point2D(6, 6))
        >>> len(_filler.inside)
        0
        >>> len(_filler.outside) > 0
        True
        >>> _filler = LagoonFiller.from_lagoon(_lagoon).flood(Point2D(1, 1))
        >>> sorted(_filler.inside)
        [Point2D(x=1, y=1), Point2D(x=1, y=6),
            Point2D(x=2, y=1), Point2D(x=2, y=6), Point2D(x=2, y=7), Point2D(x=2, y=8),
            Point2D(x=3, y=1), Point2D(x=3, y=2), Point2D(x=3, y=3), Point2D(x=3, y=4), Point2D(x=3, y=5),
            Point2D(x=3, y=6), Point2D(x=3, y=7), Point2D(x=3, y=8),
            Point2D(x=4, y=1), Point2D(x=4, y=2), Point2D(x=4, y=3), Point2D(x=4, y=4), Point2D(x=4, y=8),
            Point2D(x=5, y=1), Point2D(x=5, y=2), Point2D(x=5, y=3), Point2D(x=5, y=4), Point2D(x=5, y=8)]
        >>> len(_filler.outside)
        0
        """
        if self.is_outside(start):
            self.outside.add(start)
            return self
        if start in self.inside:
            return self
        if start in self.lagoon.holes:
            return self
        visited: Set[Point2D] = {start}
        stack: List[Point2D] = [start]
        while stack:
            position = stack.pop(0)
            for neighbour in position.get_manhattan_neighbours():
                if self.is_outside(neighbour):
                    self.outside.add(neighbour)
                    self.outside.update(visited)
                    return self
                if neighbour in self.inside:
                    continue
                if neighbour in self.lagoon.holes:
                    continue
                if neighbour in visited:
                    continue
                stack.append(neighbour)
                visited.add(neighbour)
        self.inside.update(visited)
        return self

    def is_outside(self, position: Point2D) -> bool:
        if position in self.outside:
            return True
        (min_x, min_y), (max_x, max_y) = self.boundaries
        if not (min_x <= position.x <= max_x and min_y <= position.y <= max_y):
            return True
        return False


DigInstructionT = TypeVar("DigInstructionT", bound="TypeVar")


@dataclass
class DigInstructionSet(Generic[DigInstructionT]):
    instructions: List[DigInstructionT]

    @classmethod
    def get_dig_instruction_class(cls) -> Type[DigInstructionT]:
        return get_type_argument_class(cls, DigInstructionT)

    @classmethod
    def from_instructions_text(cls: "DigInstructionSet", text: str) -> "DigInstructionSet":
        """
        >>> print(DigInstructionSet.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... '''))
        R 6 (#70c710)
        D 5 (#0dc571)
        L 2 (#5713f0)
        D 2 (#d2c081)
        R 2 (#59c680)
        D 2 (#411b91)
        L 5 (#8ceee2)
        U 2 (#caa173)
        L 1 (#1b58a2)
        U 2 (#caa171)
        R 2 (#7807d2)
        U 3 (#a77fa3)
        L 2 (#015232)
        U 2 (#7a21e3)
        """
        dig_instruction_class = cls.get_dig_instruction_class()
        return cls(instructions=list(map(dig_instruction_class.from_instruction_text, text.strip().splitlines())))

    def __str__(self) -> str:
        return "\n".join(map(str, self.instructions))

    def dig(self, lagoon: Optional[Lagoon] = None) -> "Lagoon":
        """
        >>> print(DigInstructionSet.from_instructions_text('''
        ...     R 6 (#70c710)
        ...     D 5 (#0dc571)
        ...     L 2 (#5713f0)
        ...     D 2 (#d2c081)
        ...     R 2 (#59c680)
        ...     D 2 (#411b91)
        ...     L 5 (#8ceee2)
        ...     U 2 (#caa173)
        ...     L 1 (#1b58a2)
        ...     U 2 (#caa171)
        ...     R 2 (#7807d2)
        ...     U 3 (#a77fa3)
        ...     L 2 (#015232)
        ...     U 2 (#7a21e3)
        ... ''').dig())
        #######
        #.....#
        ###...#
        ..#...#
        ..#...#
        ###.###
        #...#..
        ##..###
        .#....#
        .######
        """
        if lagoon is None:
            lagoon = Lagoon.empty()
        position = Point2D(0, 0)
        for instruction in self.instructions:
            offset = instruction.direction.offset
            for _ in range(instruction.amount):
                position = position.offset(offset)
                lagoon.add(position)
        return lagoon


@dataclass
class DigInstruction:
    direction: Direction
    amount: int
    colour: str

    re_instruction: ClassVar[re.Pattern] = re.compile(r'^([UDLR]) (\d+) \(#([0-9a-f]+)\)$')
    direction_map: ClassVar[Dict[str, Direction]] = {
        "U": Direction.Up,
        "D": Direction.Down,
        "L": Direction.Left,
        "R": Direction.Right,
    }
    direction_display_map: ClassVar[Dict[Direction, str]] = {
        direction: text
        for text, direction in direction_map.items()
    }

    @classmethod
    def from_instruction_text(cls, text: str) -> "DigInstruction":
        """
        >>> print(DigInstruction.from_instruction_text('R 6 (#70c710)'))
        R 6 (#70c710)
        """
        direction_str, amount_str, colour = cls.re_instruction.match(text.strip()).groups()
        return cls(direction=cls.direction_map[direction_str], amount=int(amount_str), colour=colour)

    def __str__(self) -> str:
        return f"{self.direction_display_map[self.direction]} {self.amount} (#{self.colour})"


Challenge.main()
challenge = Challenge()
