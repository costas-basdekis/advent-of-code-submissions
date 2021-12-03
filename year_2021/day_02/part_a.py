#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, List

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        2019945
        """
        position = InstructionSet.from_instructions_text(_input).travel()
        return position.x * position.y


@dataclass
class InstructionSet:
    instructions: List["Instruction"]

    @classmethod
    def from_instructions_text(cls, instructions_text: str) -> "InstructionSet":
        """
        >>> InstructionSet.from_instructions_text(
        ...     "forward 5\\n"
        ...     "down 5\\n"
        ...     "forward 8\\n"
        ...     "up 3\\n"
        ...     "down 8\\n"
        ...     "forward 2\\n"
        ... )
        InstructionSet(instructions=[ForwardInstruction(offset=Point2D(x=5, y=0)),
            DownInstruction(offset=Point2D(x=0, y=5)),
            ForwardInstruction(offset=Point2D(x=8, y=0)),
            UpInstruction(offset=Point2D(x=0, y=-3)),
            DownInstruction(offset=Point2D(x=0, y=8)),
            ForwardInstruction(offset=Point2D(x=2, y=0))])
        """
        return cls(
            instructions=list(map(
                Instruction.parse,
                instructions_text.splitlines(),
            )),
        )

    def travel(self) -> "Position":
        return self.travel_from(Point2D.get_zero_point())

    def travel_from(self, position: "Position") -> "Position":
        """
        >>> InstructionSet.from_instructions_text(
        ...     "forward 5\\n"
        ...     "down 5\\n"
        ...     "forward 8\\n"
        ...     "up 3\\n"
        ...     "down 8\\n"
        ...     "forward 2\\n"
        ... ).travel_from(Point2D.get_zero_point())
        Point2D(x=15, y=10)
        """
        current = position
        for instruction in self.instructions:
            current = instruction.travel(current)

        return current


Position = Point2D
Offset = Point2D


class Instruction(PolymorphicParser, ABC, root=True):
    """
    >>> Instruction.parse("forward 5")
    ForwardInstruction(offset=Point2D(x=5, y=0))
    >>> Instruction.parse("down 5")
    DownInstruction(offset=Point2D(x=0, y=5))
    >>> Instruction.parse("up 5")
    UpInstruction(offset=Point2D(x=0, y=-5))
    """

    def travel(self, position: Position) -> Position:
        raise NotImplementedError()


@dataclass
class SimpleInstruction(Instruction, ABC):
    unit_offset: ClassVar[Offset]
    offset: Offset

    re_instruction = re.compile(r"^([^\s]+) (\d+)$")

    @classmethod
    def try_parse(cls, text: str):
        match = cls.re_instruction.match(text)
        if not match:
            return None

        direction, amount_str = match.groups()
        if direction != cls.name:
            return None

        amount = int(amount_str)
        offset_x, offset_y = cls.unit_offset
        # noinspection PyArgumentList
        return cls(offset=Point2D(amount * offset_x, amount * offset_y))

    def travel(self, position: Position) -> Position:
        return position.offset(self.offset)


@Instruction.register
class ForwardInstruction(SimpleInstruction):
    """
    >>> ForwardInstruction.try_parse("forward 5")
    ForwardInstruction(offset=Point2D(x=5, y=0))
    """
    name = "forward"
    unit_offset = (1, 0)


@Instruction.register
class DownInstruction(SimpleInstruction):
    """
    >>> DownInstruction.try_parse("down 5")
    DownInstruction(offset=Point2D(x=0, y=5))
    """
    name = "down"
    unit_offset = (0, 1)


@Instruction.register
class UpInstruction(SimpleInstruction):
    """
    >>> UpInstruction.try_parse("up 5")
    UpInstruction(offset=Point2D(x=0, y=-5))
    """
    name = "up"
    unit_offset = (0, -1)


Challenge.main()
challenge = Challenge()
