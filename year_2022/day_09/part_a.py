#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import ClassVar, Dict, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        6057
        """
        rope = Rope()\
            .move_on_instructions(
                InstructionSet.from_instructions_text(_input),
            )
        debugger.report(rope.get_history_diagram())
        return rope.tail_history_length


@dataclass
class Rope:
    head: Point2D = field(default=Point2D.get_zero_point())
    tail: Point2D = field(default=Point2D.get_zero_point())
    tail_history: Set[Point2D] = field(default_factory=set)

    gap_move: ClassVar[Dict[Point2D, Point2D]]

    def __post_init__(self):
        self.tail_history.add(self.tail)

    @property
    def gap(self) -> Point2D:
        return self.head.difference(self.tail)

    @property
    def tail_history_length(self) -> int:
        """
        >>> Rope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 4\\n"
        ...     "U 4\\n"
        ...     "L 3\\n"
        ...     "D 1\\n"
        ...     "R 4\\n"
        ...     "D 1\\n"
        ...     "L 5\\n"
        ...     "R 2"
        ... )).tail_history_length
        13
        """
        return len(self.tail_history)

    def move_on_instructions(self, instructions: "InstructionSet") -> "Rope":
        """
        >>> print(str(Rope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 4\\n"
        ...     "U 4\\n"
        ...     "L 3\\n"
        ...     "D 1\\n"
        ...     "R 4\\n"
        ...     "D 1\\n"
        ...     "L 5\\n"
        ...     "R 2"
        ... ))))
        .TH
        ...
        s..
        >>> print(Rope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 4\\n"
        ...     "U 4\\n"
        ...     "L 3\\n"
        ...     "D 1\\n"
        ...     "R 4\\n"
        ...     "D 1\\n"
        ...     "L 5\\n"
        ...     "R 2"
        ... )).get_history_diagram())
        ..##.
        ...##
        .####
        ....#
        s###.
        """
        for instruction in instructions.instructions:
            self.move(instruction.direction, instruction.amount)
        return self

    def move_on_instruction(self, instruction: "Instruction") -> "Rope":
        return self.move(instruction.direction, instruction.amount)

    def move(self, direction: "Direction", amount: int) -> "Rope":
        """
        >>> print(str(Rope().move(Direction.Right, 1)))
        TH
        >>> print(str(Rope().move(Direction.Right, 1).move(Direction.Right, 1)))
        sTH
        >>> print(str(Rope().move(Direction.Right, 1).move(Direction.Right, 1).move(Direction.Right,1 )))
        s.TH
        >>> print(str(Rope().move(Direction.Right, 2)))
        sTH
        >>> print(str(Rope().move(Direction.Right, 3)))
        s.TH
        >>> print(str(Rope().move(Direction.Right, 1).move(Direction.Down, 1)))
        T.
        .H
        >>> print(str(Rope().move(Direction.Right, 1).move(Direction.Down, 1).move(Direction.Right, 1)))
        s..
        .TH
        """
        for _ in range(amount):
            self.head = self.head.offset(direction.offset)
            gap = self.gap
            self.tail = self.tail.offset(self.gap_move[gap])
            self.tail_history.add(self.tail)

        return self

    def __str__(self) -> str:
        """
        >>> print(str(Rope()))
        H
        >>> print(str(Rope(head=Point2D(1, 0), tail=Point2D(0, 0))))
        TH
        """
        start = Point2D.get_zero_point()
        points = [start, self.head, self.tail]
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(points)
        return "\n".join(
            "".join(
                "H"
                if point == self.head else
                "T"
                if point == self.tail else
                "s"
                if point == start else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    def get_history_diagram(self) -> str:
        start = Point2D.get_zero_point()
        (min_x, min_y), (max_x, max_y) = \
            min_and_max_tuples({start} | self.tail_history)
        return "\n".join(
            "".join(
                "s"
                if point == start else
                "#"
                if point in self.tail_history else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )


Rope.gap_move = {
    Point2D.get_zero_point(): Point2D.get_zero_point(),
    **{
        Point2D(offset): Point2D.get_zero_point()
        for offset in Point2D.get_zero_point().get_euclidean_offsets()
    },
    **{
        Point2D(offset): Point2D(offset).sign()
        for offset in Point2D.get_zero_point().get_euclidean_offsets_of(2)
    },
}


@dataclass
class InstructionSet:
    instructions: ["Instruction"]

    @classmethod
    def from_instructions_text(cls, instructions_text: str) -> "InstructionSet":
        """
        >>> InstructionSet.from_instructions_text(
        ...     "R 4\\n"
        ...     "U 4\\n"
        ...     "L 3\\n"
        ...     "D 1\\n"
        ...     "R 4\\n"
        ...     "D 1\\n"
        ...     "L 5\\n"
        ...     "R 2"
        ... )
        InstructionSet(instructions=[Instruction(direction=Direction.Right, amount=4), ...])
        """
        return cls(
            instructions=list(map(
                Instruction.from_instruction_text,
                instructions_text.strip().splitlines(),
            )),
        )


class Direction(Enum):
    Up = "up"
    Down = "down"
    Left = "left"
    Right = "right"

    parse_map: Dict[str, "Direction"]
    offset_map: Dict["Direction", Point2D]

    @classmethod
    def from_direction_text(cls, direction_text: str) -> "Direction":
        return cls.parse_map[direction_text]

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    @property
    def offset(self) -> Point2D:
        return self.offset_map[self]


Direction.parse_map = {
    "U": Direction.Up,
    "D": Direction.Down,
    "L": Direction.Left,
    "R": Direction.Right,
}
Direction.offset_map = {
    Direction.Up: Point2D(0, -1),
    Direction.Down: Point2D(0, 1),
    Direction.Left: Point2D(-1, 0),
    Direction.Right: Point2D(1, 0),
}


@dataclass
class Instruction:
    direction: Direction
    amount: int

    re_instruction = re.compile(r"^([LRUD]) (\d+)$")

    @classmethod
    def from_instruction_text(cls, instruction_text: str) -> "Instruction":
        """
        >>> Instruction.from_instruction_text("R 1")
        Instruction(direction=Direction.Right, amount=1)
        >>> Instruction.from_instruction_text("L 3")
        Instruction(direction=Direction.Left, amount=3)
        >>> Instruction.from_instruction_text("D 259")
        Instruction(direction=Direction.Down, amount=259)
        >>> Instruction.from_instruction_text("U 10")
        Instruction(direction=Direction.Up, amount=10)
        """
        direction_str, amount_str = \
            cls.re_instruction.match(instruction_text).groups()
        return cls(
            direction=Direction.from_direction_text(direction_str),
            amount=int(amount_str),
        )


Challenge.main()
challenge = Challenge()
