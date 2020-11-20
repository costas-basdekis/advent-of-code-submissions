#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Type, TypeVar, Generic

from aox.utils import StringEnum
from utils import Point2D, BaseChallenge, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        288
        """
        return Walker.get_instructions_distance_from_text(_input)


# noinspection PyTypeChecker
InstructionSetT = TypeVar('InstructionSetT', bound='InstructionSet')


@dataclass
class Walker(Generic[InstructionSetT]):
    position: Point2D = Point2D.get_zero_point()
    direction: 'Instruction.Direction' = \
        field(default_factory=lambda: Instruction.Direction.Up)

    @classmethod
    def get_instruction_set_class(cls) -> Type[InstructionSetT]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, InstructionSetT)

    @classmethod
    def get_instructions_distance_from_text(cls, instructions_text: str) \
            -> int:
        """
        >>> Walker.get_instructions_distance_from_text('R2, L3')
        5
        >>> Walker.get_instructions_distance_from_text('R2, R2, R2')
        2
        >>> Walker.get_instructions_distance_from_text('R5, L5, R5, R3')
        12
        """
        instruction_set = cls.get_instruction_set_class()\
            .from_instructions_text(instructions_text)
        return cls().move(instruction_set).get_distance()

    @classmethod
    def get_instructions_distance(cls, instruction_set: InstructionSetT) \
            -> int:
        return cls().move(instruction_set).get_distance()

    def move(self, instruction_set: InstructionSetT):
        """
        >>> Walker(Point2D(2, 3), Instruction.Direction.Right)\\
        ...     .move(InstructionSet([
        ...         Instruction(Instruction.Turn.Right, 10),
        ...         Instruction(Instruction.Turn.Left, 10),
        ...     ]))
        Walker(position=Point2D(x=12, y=13), direction=Direction.Right)
        """
        self.position, self.direction = instruction_set\
            .move(self.position, self.direction)

        return self

    def get_distance(self) -> int:
        return self.position.manhattan_length()


# noinspection PyTypeChecker
InstructionT = TypeVar('InstructionT', bound='Instruction')


class InstructionSet(Generic[InstructionT]):
    @classmethod
    def get_instruction_class(cls) -> Type[InstructionT]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, InstructionT)

    @classmethod
    def from_instructions_text(cls, text: str):
        """
        >>> InstructionSet.from_instructions_text("R4, R3, L3, L2").instructions
        [Instruction(turn=Turn.Right, move_amount=4),
            Instruction(turn=Turn.Right, move_amount=3),
            Instruction(turn=Turn.Left, move_amount=3),
            Instruction(turn=Turn.Left, move_amount=2)]
        """
        return cls(list(map(
            cls.get_instruction_class().from_instruction_text,
            text.split(', '))))

    def __init__(self, instructions):
        self.instructions: List[InstructionT] = instructions

    def move(self, position: Point2D, direction: 'Instruction.Direction') \
            -> Tuple[Point2D, 'Instruction.Direction']:
        """
        >>> InstructionSet([
        ...     Instruction(Instruction.Turn.Left, 10),
        ... ]).move(Point2D(2, 3), Instruction.Direction.Up)
        (Point2D(x=-8, y=3), Direction.Left)
        >>> InstructionSet([
        ...     Instruction(Instruction.Turn.Left, 10),
        ... ]).move(Point2D(2, 3), Instruction.Direction.Down)
        (Point2D(x=12, y=3), Direction.Right)
        >>> InstructionSet([
        ...     Instruction(Instruction.Turn.Right, 10),
        ... ]).move(Point2D(2, 3), Instruction.Direction.Left)
        (Point2D(x=2, y=-7), Direction.Up)
        >>> InstructionSet([
        ...     Instruction(Instruction.Turn.Right, 10),
        ... ]).move(Point2D(2, 3), Instruction.Direction.Right)
        (Point2D(x=2, y=13), Direction.Down)
        >>> InstructionSet([
        ...     Instruction(Instruction.Turn.Right, 10),
        ...     Instruction(Instruction.Turn.Left, 10),
        ... ]).move(Point2D(2, 3), Instruction.Direction.Right)
        (Point2D(x=12, y=13), Direction.Right)
        """
        for instruction in self.instructions:
            position, direction = instruction.move(position, direction)

        return position, direction


@dataclass
class Instruction:
    class Turn(Enum):
        Left = "L"
        Right = "R"

        def __repr__(self):
            return f"{type(self).__name__}.{self.name}"

    class Direction(StringEnum):
        Up = auto()
        Down = auto()
        Left = auto()
        Right = auto()

        def __repr__(self):
            return f"{type(self).__name__}.{self.name}"

    turn: Turn
    move_amount: int

    re_instruction = re.compile(r"^([LR])(\d+)$")

    # noinspection PyArgumentList
    OFFSETS = {
        Direction.Up: Point2D(0, -1),
        Direction.Down: Point2D(0, 1),
        Direction.Left: Point2D(-1, 0),
        Direction.Right: Point2D(1, 0),
    }
    LEFT_ROTATION = [
        Direction.Up,
        Direction.Left,
        Direction.Down,
        Direction.Right,
    ]

    @classmethod
    def from_instruction_text(cls, text: str):
        """
        >>> Instruction.from_instruction_text("R4")
        Instruction(turn=Turn.Right, move_amount=4)
        >>> Instruction.from_instruction_text("L15")
        Instruction(turn=Turn.Left, move_amount=15)
        """
        turn_str, move_str = cls.re_instruction.match(text).groups()

        return cls(turn=cls.Turn(turn_str), move_amount=int(move_str))

    def move(self, position: Point2D, direction: Direction) \
            -> Tuple[Point2D, Direction]:
        """
        >>> Instruction(Instruction.Turn.Left, 10)\\
        ...     .move(Point2D(2, 3), Instruction.Direction.Up)
        (Point2D(x=-8, y=3), Direction.Left)
        >>> Instruction(Instruction.Turn.Left, 10)\\
        ...     .move(Point2D(2, 3), Instruction.Direction.Down)
        (Point2D(x=12, y=3), Direction.Right)
        >>> Instruction(Instruction.Turn.Right, 10)\\
        ...     .move(Point2D(2, 3), Instruction.Direction.Left)
        (Point2D(x=2, y=-7), Direction.Up)
        >>> Instruction(Instruction.Turn.Right, 10)\\
        ...     .move(Point2D(2, 3), Instruction.Direction.Right)
        (Point2D(x=2, y=13), Direction.Down)
        """
        direction_index = self.LEFT_ROTATION.index(direction)
        if self.turn == self.Turn.Left:
            direction_index += 1
        else:
            direction_index -= 1
        final_direction = \
            self.LEFT_ROTATION[direction_index % len(self.LEFT_ROTATION)]
        final_position = position.offset(
            self.OFFSETS[final_direction], self.move_amount)
        return final_position, final_direction


Challenge.main()
challenge = Challenge()
