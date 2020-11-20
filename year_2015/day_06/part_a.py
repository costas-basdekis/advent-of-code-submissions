#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass, field
from typing import Set, List, Generic, Type, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser, Point2D, TV, \
    get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        543903
        """
        return InstructionSet.from_instructions_text(_input)\
            .apply(debugger=debugger)\
            .get_on_count()


@dataclass
class Matrix:
    points: Set[Point2D] = field(default_factory=lambda: {
        Point2D(x, y)
        for x in range(1000)
        for y in range(1000)
    })
    on: Set[Point2D] = field(default_factory=set)

    def __getitem__(self, item: Point2D) -> bool:
        return item in self.on

    def __setitem__(self, key: Point2D, value: bool):
        if key not in self.points:
            raise KeyError(key)
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool but got {repr(value)}")

        if value:
            self.on.add(key)
        else:
            if key in self.on:
                self.on.remove(key)

    def get_on_count(self) -> int:
        return len(self.on)


InstructionT = TV['Instruction']
MatrixT = TV['Matrix']


@dataclass
class InstructionSet(Generic[InstructionT, MatrixT]):
    instructions: List[InstructionT]

    @classmethod
    def get_instruction_class(cls) -> Type[InstructionT]:
        return get_type_argument_class(cls, InstructionT)

    @classmethod
    def get_matrix_class(cls) -> Type[MatrixT]:
        return get_type_argument_class(cls, MatrixT)

    @classmethod
    def from_instructions_text(cls, instructions_text: str):
        """
        >>> InstructionSet.from_instructions_text("turn on 0,0 through 999,999")
        InstructionSet(instructions=[Turn(on=True,
            start=Point2D(x=0, y=0), end=Point2D(x=999, y=999))])
        """
        instruction_class = cls.get_instruction_class()
        return cls(list(map(
            instruction_class.parse, instructions_text.splitlines())))

    def apply(self, matrix: Optional[MatrixT] = None,
              debugger: Debugger = Debugger(enabled=False)) -> MatrixT:
        """
        >>> InstructionSet.from_instructions_text(
        ...     "turn on 0,0 through 999,999").apply().get_on_count()
        1000000
        """
        if matrix is None:
            matrix_class = self.get_matrix_class()
            matrix = matrix_class()
        debugger.reset()
        for instruction in debugger.stepping(self.instructions):
            instruction.apply(matrix)
            debugger.default_report_if()
        return matrix


class Instruction(PolymorphicParser, ABC, root=True):
    def apply(self, matrix: Matrix) -> Matrix:
        raise NotImplementedError()


@Instruction.register
@dataclass
class Toggle(Instruction):
    name = 'toggle'

    start: Point2D
    end: Point2D

    re_toggle = re.compile(r"^toggle (\d+),(\d+) through (\d+),(\d+)")

    @classmethod
    def try_parse(cls, text: str):
        """
        >>> Toggle.try_parse("toggle 461,550 through 564,900")
        Toggle(start=Point2D(x=461, y=550), end=Point2D(x=564, y=900))
        >>> Instruction.parse("toggle 461,550 through 564,900")
        Toggle(start=Point2D(x=461, y=550), end=Point2D(x=564, y=900))
        """
        match = cls.re_toggle.match(text)
        if not match:
            return None
        start_x, start_y, end_x, end_y = map(int, match.groups())
        return cls(Point2D(start_x, start_y), Point2D(end_x, end_y))

    def apply(self, matrix: Matrix) -> Matrix:
        for x in range(self.start.x, self.end.x + 1):
            for y in range(self.start.y, self.end.y + 1):
                matrix[Point2D(x, y)] = not matrix[Point2D(x, y)]

        return matrix


@Instruction.register
@dataclass
class Turn(Instruction):
    name = 'turn'

    on: bool
    start: Point2D
    end: Point2D

    re_toggle = re.compile(r"^turn (on|off) (\d+),(\d+) through (\d+),(\d+)")

    ON_MAP = {
        "on": True,
        "off": False,
    }

    @classmethod
    def try_parse(cls, text: str):
        """
        >>> Turn.try_parse("turn off 370,39 through 425,839")
        Turn(on=False, start=Point2D(x=370, y=39), end=Point2D(x=425, y=839))
        >>> Turn.try_parse("turn on 370,39 through 425,839")
        Turn(on=True, start=Point2D(x=370, y=39), end=Point2D(x=425, y=839))
        >>> Instruction.parse("turn off 370,39 through 425,839")
        Turn(on=False, start=Point2D(x=370, y=39), end=Point2D(x=425, y=839))
        >>> Instruction.parse("turn on 370,39 through 425,839")
        Turn(on=True, start=Point2D(x=370, y=39), end=Point2D(x=425, y=839))
        """
        match = cls.re_toggle.match(text)
        if not match:
            return None
        on_str, *coordinate_strs = match.groups()
        on = cls.ON_MAP[on_str]
        start_x, start_y, end_x, end_y = map(int, coordinate_strs)
        return cls(on, Point2D(start_x, start_y), Point2D(end_x, end_y))

    def apply(self, matrix: Matrix) -> Matrix:
        for x in range(self.start.x, self.end.x + 1):
            for y in range(self.start.y, self.end.y + 1):
                matrix[Point2D(x, y)] = self.on

        return matrix


Challenge.main()
challenge = Challenge()
