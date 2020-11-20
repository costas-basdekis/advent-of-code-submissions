#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, Generic, List, Type, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, TV, get_type_argument_class, \
    PolymorphicParser


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        14687245
        """
        return InstructionSet.from_instructions_text(_input)\
            .apply(debugger=debugger)\
            .get_brightness_total()


@dataclass
class Matrix:
    brightness: Dict[Point2D, int] = \
        field(default_factory=lambda: {
            Point2D(x, y): 0
            for x in range(1000)
            for y in range(1000)
        })

    def __getitem__(self, item: Point2D) -> int:
        return self.brightness.get(item, 0)

    def __setitem__(self, key: Point2D, value: int):
        if key not in self.brightness:
            raise KeyError(key)
        if not isinstance(value, int):
            raise TypeError(f"Expected int but got {repr(value)}")

        self.brightness[key] = max(0, value)

    def get_brightness_total(self) -> int:
        return sum(self.brightness.values())


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
        InstructionSet(instructions=[Turn(offset=1,
            start=Point2D(x=0, y=0), end=Point2D(x=999, y=999))])
        """
        instruction_class = cls.get_instruction_class()
        return cls(list(map(
            instruction_class.parse, instructions_text.splitlines())))

    def apply(self, matrix: Optional[MatrixT] = None,
              debugger: Debugger = Debugger(enabled=False)) -> MatrixT:
        """
        >>> InstructionSet.from_instructions_text(
        ...     "turn on 0,0 through 999,999").apply().get_brightness_total()
        2000000
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
                matrix[Point2D(x, y)] += 2

        return matrix


@Instruction.register
@dataclass
class Turn(Instruction):
    name = 'turn'

    offset: int
    start: Point2D
    end: Point2D

    re_toggle = re.compile(r"^turn (on|off) (\d+),(\d+) through (\d+),(\d+)")

    ON_MAP = {
        "on": 1,
        "off": -1,
    }

    @classmethod
    def try_parse(cls, text: str):
        """
        >>> Turn.try_parse("turn off 370,39 through 425,839")
        Turn(offset=-1, start=Point2D(x=370, y=39), end=Point2D(x=425, y=839))
        >>> Turn.try_parse("turn on 370,39 through 425,839")
        Turn(offset=1, start=Point2D(x=370, y=39), end=Point2D(x=425, y=839))
        >>> Instruction.parse("turn off 370,39 through 425,839")
        Turn(offset=-1, start=Point2D(x=370, y=39), end=Point2D(x=425, y=839))
        >>> Instruction.parse("turn on 370,39 through 425,839")
        Turn(offset=1, start=Point2D(x=370, y=39), end=Point2D(x=425, y=839))
        """
        match = cls.re_toggle.match(text)
        if not match:
            return None
        offset_str, *coordinate_strs = match.groups()
        offset = cls.ON_MAP[offset_str]
        start_x, start_y, end_x, end_y = map(int, coordinate_strs)
        return cls(offset, Point2D(start_x, start_y), Point2D(end_x, end_y))

    def apply(self, matrix: Matrix) -> Matrix:
        for x in range(self.start.x, self.end.x + 1):
            for y in range(self.start.y, self.end.y + 1):
                matrix[Point2D(x, y)] += self.offset

        return matrix


Challenge.main()
challenge = Challenge()
