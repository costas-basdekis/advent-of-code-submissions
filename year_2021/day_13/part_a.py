#!/usr/bin/env python3
import re
from dataclasses import dataclass
from enum import Enum
from typing import Set, Generic, List, Type, Union, Tuple

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, TV, get_type_argument_class, \
    min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        847
        """
        return FoldInstructionSet\
            .fold_once_from_sheet_and_instructions_text(_input)\
            .dot_count


class FoldAxisEnum(Enum):
    X = "X"
    Y = "Y"

    @classmethod
    def from_axis_text(cls, axis_text: str) -> "FoldAxisEnum":
        """
        >>> FoldAxisEnum.from_axis_text("   x   ")
        FoldAxisEnum.X
        >>> FoldAxisEnum.from_axis_text("x")
        FoldAxisEnum.X
        >>> FoldAxisEnum.from_axis_text("X")
        FoldAxisEnum.X
        """
        return cls(axis_text.upper().strip())

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


SheetT = TV["Sheet"]
FoldInstructionT = TV["FoldInstruction"]


@dataclass
class FoldInstructionSet(Generic[SheetT, FoldInstructionT]):
    instructions: List[FoldInstructionT]

    @classmethod
    def get_sheet_class(cls) -> Type[SheetT]:
        return get_type_argument_class(cls, SheetT)

    @classmethod
    def get_instruction_class(cls) -> Type[FoldInstructionT]:
        return get_type_argument_class(cls, FoldInstructionT)

    @classmethod
    def fold_once_from_sheet_and_instructions_text(
        cls, text: str,
    ) -> SheetT:
        """
        >>> FoldInstructionSet.fold_once_from_sheet_and_instructions_text('''
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ...
        ...     fold along y=7
        ...     fold along x=5
        ... ''').dot_count
        17
        """
        sheet, instructions = cls.from_sheet_and_instructions_text(text)
        return instructions.fold_once(sheet)

    @classmethod
    def fold_from_sheet_and_instructions_text(
        cls, text: str,
    ) -> SheetT:
        sheet, instructions = cls.from_sheet_and_instructions_text(text)
        return instructions.fold(sheet)

    @classmethod
    def from_sheet_and_instructions_text(
        cls, text: str,
    ) -> Tuple[SheetT, "FoldInstructionSet"]:
        """
        >>> sheet, instructions = FoldInstructionSet.from_sheet_and_instructions_text('''
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ...
        ...     fold along y=7
        ...     fold along x=5
        ... ''')
        >>> print(":", sheet)
        : ...#..#..#.
        ....#......
        ...........
        #..........
        ...#....#.#
        ...........
        ...........
        ...........
        ...........
        ...........
        .#....#.##.
        ....#......
        ......#...#
        #..........
        #.#........
        >>> instructions
        FoldInstructionSet(instructions=[FoldInstruction(axis=FoldAxisEnum.Y,
            coordinate=7),
            FoldInstruction(axis=FoldAxisEnum.X, coordinate=5)])
        """
        sheet_text, instructions_text = text.split("\n\n")
        return (
            cls.get_sheet_class().from_sheet_text(sheet_text),
            cls.from_instructions_text(instructions_text),
        )

    @classmethod
    def from_instructions_text(
        cls, instructions_text: str,
    ) -> "FoldInstructionSet":
        """
        >>> FoldInstructionSet.from_instructions_text('''
        ...     fold along y=7
        ...     fold along x=5
        ... ''')
        FoldInstructionSet(instructions=[FoldInstruction(axis=FoldAxisEnum.Y,
            coordinate=7),
            FoldInstruction(axis=FoldAxisEnum.X, coordinate=5)])
        """
        instruction_class = cls.get_instruction_class()
        return cls(
            instructions=list(map(
                instruction_class.from_instruction_text,
                filter(None, map(str.strip, instructions_text.splitlines())),
            )),
        )

    def fold_once(self, sheet: "Sheet") -> "Sheet":
        """
        >>> instruction_set = FoldInstructionSet.from_instructions_text('''
        ...     fold along y=7
        ...     fold along x=5
        ... ''')
        >>> _sheet = Sheet.from_sheet_text('''
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ... ''')
        >>> print(":", instruction_set.fold_once(_sheet))
        : #.##..#..#.
        #...#......
        ......#...#
        #...#......
        .#.#..#.###
        """
        return self.instructions[0].fold(sheet)

    def fold(self, sheet: "Sheet") -> "Sheet":
        """
        >>> instruction_set = FoldInstructionSet.from_instructions_text('''
        ...     fold along y=7
        ...     fold along x=5
        ... ''')
        >>> _sheet = Sheet.from_sheet_text('''
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ... ''')
        >>> print(":", instruction_set.fold(_sheet))
        : #####
        #...#
        #...#
        #...#
        #####
        """
        result = sheet
        for instruction in self.instructions:
            result = instruction.fold(result)

        return result


FoldAxisEnumT = TV["FoldAxisEnum"]


@dataclass
class FoldInstruction(Generic[FoldAxisEnumT]):
    axis: FoldAxisEnum
    coordinate: int

    re_instruction = re.compile(r"^fold along ([xy])=(\d+)$")

    @classmethod
    def get_axis_class(cls) -> Type[FoldAxisEnumT]:
        return get_type_argument_class(cls, FoldAxisEnumT)

    @classmethod
    def from_instruction_text(cls, instruction_text: str) -> "FoldInstruction":
        """
        >>> FoldInstruction.from_instruction_text("fold along y=13")
        FoldInstruction(axis=FoldAxisEnum.Y, coordinate=13)
        """
        axis_str, coordinate_str = \
            cls.re_instruction.match(instruction_text).groups()
        axis_class = cls.get_axis_class()
        return cls(
            axis=axis_class.from_axis_text(axis_str.upper()),
            coordinate=int(coordinate_str),
        )

    def fold(self, sheet: "Sheet") -> "Sheet":
        """
        >>> _sheet = Sheet.from_sheet_text('''
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ... ''')
        >>> _sheet = FoldInstruction(FoldAxisEnum.Y, 7).fold(_sheet)
        >>> print(":", _sheet)
        : #.##..#..#.
        #...#......
        ......#...#
        #...#......
        .#.#..#.###
        >>> _sheet = FoldInstruction(FoldAxisEnum.X, 5).fold(_sheet)
        >>> print(":", _sheet)
        : #####
        #...#
        #...#
        #...#
        #####
        """
        sheet_class = type(sheet)
        # noinspection PyArgumentList
        return sheet_class(dots=set(map(self.transform, sheet.dots)))

    def transform(self, point: Point2D) -> Point2D:
        """
        >>> FoldInstruction(FoldAxisEnum.X, 5).transform(Point2D(3, 2))
        Point2D(x=3, y=2)
        >>> FoldInstruction(FoldAxisEnum.X, 5).transform(Point2D(5, 2))
        Traceback (most recent call last):
        ...
        Exception: Points are not supposed to be on folding axis: ...
        >>> FoldInstruction(FoldAxisEnum.X, 5).transform(Point2D(6, 2))
        Point2D(x=4, y=2)
        >>> FoldInstruction(FoldAxisEnum.Y, 5).transform(Point2D(2, 3))
        Point2D(x=2, y=3)
        >>> FoldInstruction(FoldAxisEnum.Y, 5).transform(Point2D(2, 5))
        Traceback (most recent call last):
        ...
        Exception: Points are not supposed to be on folding axis: ...
        >>> FoldInstruction(FoldAxisEnum.Y, 5).transform(Point2D(2, 6))
        Point2D(x=2, y=4)
        """
        if self.axis == FoldAxisEnum.X:
            if point.x == self.coordinate:
                raise Exception(
                    f"Points are not supposed to be on folding axis: {point} "
                    f"is on {self}"
                )
            if point.x < self.coordinate:
                return point

            offset = point.x - self.coordinate
            return Point2D(self.coordinate - offset, point.y)
        elif self.axis == FoldAxisEnum.Y:
            if point.y == self.coordinate:
                raise Exception(
                    f"Points are not supposed to be on folding axis: {point} "
                    f"is on {self}"
                )
            if point.y < self.coordinate:
                return point

            offset = point.y - self.coordinate
            return Point2D(point.x, self.coordinate - offset)
        else:
            raise Exception(f"Unknown folding axis {self.axis}")


@dataclass
class Sheet:
    dots: Set[Point2D]

    @classmethod
    def from_sheet_text(cls, sheet_text: str) -> "Sheet":
        """
        >>> sorted(Sheet.from_sheet_text('''
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ... ''').dots)
        [Point2D(x=0, y=3), Point2D(x=0, y=13), Point2D(x=0, y=14),
            Point2D(x=1, y=10), Point2D(x=2, y=14), Point2D(x=3, y=0),
            Point2D(x=3, y=4), Point2D(x=4, y=1), Point2D(x=4, y=11),
            Point2D(x=6, y=0), Point2D(x=6, y=10), Point2D(x=6, y=12),
            Point2D(x=8, y=4), Point2D(x=8, y=10), Point2D(x=9, y=0),
            Point2D(x=9, y=10), Point2D(x=10, y=4), Point2D(x=10, y=12)]
        >>> print(":", Sheet.from_sheet_text('''
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ... '''))
        : ...#..#..#.
        ....#......
        ...........
        #..........
        ...#....#.#
        ...........
        ...........
        ...........
        ...........
        ...........
        .#....#.##.
        ....#......
        ......#...#
        #..........
        #.#........
        """
        return cls(
            dots={
                Point2D(int(x_str), int(y_str))
                for line
                in filter(None, map(str.strip, sheet_text.splitlines()))
                for x_str, y_str in [line.split(",")]
            },
        )

    @classmethod
    def from_printed_sheet(cls, sheet_printout: str) -> "Sheet":
        """
        >>> print(":", Sheet.from_printed_sheet('''
        ...     #####
        ...     #...#
        ...     #...#
        ...     #...#
        ...     #####
        ... '''))
        : #####
        #...#
        #...#
        #...#
        #####
        """
        lines = filter(None, map(str.strip, sheet_printout.splitlines()))
        return cls(
            dots={
                Point2D(x, y)
                for y, line
                in enumerate(lines)
                for x, character in enumerate(line)
                if character == "#"
            },
        )

    def __str__(self) -> str:
        (min_x, max_x), (min_y, max_y) = self.get_bounding_box()
        return "\n".join(
            "".join(
                "#" if self[Point2D(x, y)] else "."
                for x in range(min_x, max_x + 1)
            )
            for y in range(min_y, max_y + 1)
        )

    def get_bounding_box(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        >>> Sheet.from_sheet_text('''
        ...     6,10
        ...     0,14
        ...     9,10
        ...     0,3
        ...     10,4
        ...     4,11
        ...     6,0
        ...     6,12
        ...     4,1
        ...     0,13
        ...     10,12
        ...     3,4
        ...     3,0
        ...     8,4
        ...     1,10
        ...     2,14
        ...     8,10
        ...     9,0
        ... ''').get_bounding_box()
        ((0, 10), (0, 14))
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.dots)
        return (min_x, max_x), (min_y, max_y)

    @property
    def dot_count(self) -> int:
        """
        >>> Sheet.from_printed_sheet('''
        ...     #.##..#..#.
        ...     #...#......
        ...     ......#...#
        ...     #...#......
        ...     .#.#..#.###
        ... ''').dot_count
        17
        """
        return len(self.dots)

    def __getitem__(self, item: Union[Point2D, Tuple]) -> bool:
        return item in self

    def __setitem__(self, key: Union[Point2D, Tuple], value: bool) -> None:
        if isinstance(key, tuple):
            key = Point2D(key)
        value = bool(value)

        if value:
            self.dots.add(key)
        else:
            if self[key]:
                self.dots.remove(key)

    def __contains__(self, item: Union[Point2D, Tuple]) -> bool:
        if isinstance(item, tuple):
            item = Point2D(item)

        return item in self.dots


Challenge.main()
challenge = Challenge()
