#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass
from typing import ClassVar

from aox.challenge import Debugger
from utils import BaseChallenge, Point3D, PolymorphicParser, Point2D
from year_2021.day_02.part_a import InstructionSet, Position


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1599311480
        """
        position = InstructionSetExtended\
            .from_instructions_text(_input)\
            .travel()
        return position.x * position.y


class InstructionSetExtended(InstructionSet["InstructionExtended"]):
    def travel(self) -> "Position":
        return self.travel_from(Position.get_zero_point())

    def travel_from(self, position: "Position") -> "Position":
        """
        >>> InstructionSetExtended.from_instructions_text(
        ...     "forward 5\\n"
        ...     "down 5\\n"
        ...     "forward 8\\n"
        ...     "up 3\\n"
        ...     "down 8\\n"
        ...     "forward 2\\n"
        ... ).travel_from(Point2D.get_zero_point())
        Point2D(x=15, y=60)
        """
        current = AimedPosition(position.x, position.y, 0)
        for instruction in self.instructions:
            current = instruction.travel(current)

        return Position(current.x, current.y)


AimedPosition = Point3D


class InstructionExtended(PolymorphicParser, ABC, root=True):
    """
    >>> InstructionExtended.parse("forward 5")
    ForwardInstructionExtended(offset=5)
    >>> InstructionExtended.parse("down 5")
    DownInstruction(aim_offset=5)
    >>> InstructionExtended.parse("up 5")
    UpInstruction(aim_offset=-5)
    """
    def travel(self, position: AimedPosition) -> AimedPosition:
        raise NotImplementedError()


@InstructionExtended.register
@dataclass
class ForwardInstructionExtended(InstructionExtended):
    """
    >>> ForwardInstructionExtended.try_parse("forward 5")
    ForwardInstructionExtended(offset=5)
    """
    name = "forward"
    offset: int

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
        # noinspection PyArgumentList
        return cls(offset=amount)

    def travel(self, position: AimedPosition) -> AimedPosition:
        """
        >>> ForwardInstructionExtended(5).travel(Point3D(0, 0, 0))
        Point3D(x=5, y=0, z=0)
        >>> ForwardInstructionExtended(5).travel(Point3D(0, 0, 3))
        Point3D(x=5, y=15, z=3)
        """
        return AimedPosition(
            x=position.x + self.offset,
            y=position.y + position.z * self.offset,
            z=position.z,
        )


@dataclass
class AimInstruction(InstructionExtended, ABC):
    unit_aim_offset: ClassVar[int]
    aim_offset: int

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
        # noinspection PyArgumentList
        return cls(aim_offset=cls.unit_aim_offset * amount)

    def travel(self, position: AimedPosition) -> AimedPosition:
        return AimedPosition(
            x=position.x,
            y=position.y,
            z=position.z + self.aim_offset,
        )


@InstructionExtended.register
class DownInstruction(AimInstruction):
    """
    >>> DownInstruction.try_parse("down 5")
    DownInstruction(aim_offset=5)
    """
    name = "down"
    unit_aim_offset = 1


@InstructionExtended.register
class UpInstruction(AimInstruction):
    """
    >>> UpInstruction.try_parse("up 5")
    UpInstruction(aim_offset=-5)
    """
    name = "up"
    unit_aim_offset = -1


Challenge.main()
challenge = Challenge()
