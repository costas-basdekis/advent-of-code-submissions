#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import ClassVar, Dict, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples
from year_2022.day_09.part_a import InstructionSet, Instruction, Direction


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2514
        """
        rope = LongRope()\
            .move_on_instructions(
                InstructionSet.from_instructions_text(_input),
            )
        debugger.report(rope.get_history_diagram())
        return rope.tail_history_length


@dataclass
class LongRope:
    head: Point2D = field(default=Point2D.get_zero_point())
    tails: [Point2D] = \
        field(default_factory=lambda: [Point2D.get_zero_point()] * 9)
    tail_history: Set[Point2D] = field(default_factory=set)

    gap_move: ClassVar[Dict[Point2D, Point2D]]

    def __post_init__(self):
        self.tail_history.add(self.tails[-1])

    @property
    def tail_history_length(self) -> int:
        """
        >>> LongRope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 4\\n"
        ...     "U 4\\n"
        ...     "L 3\\n"
        ...     "D 1\\n"
        ...     "R 4\\n"
        ...     "D 1\\n"
        ...     "L 5\\n"
        ...     "R 2"
        ... )).tail_history_length
        1
        >>> LongRope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 5\\n"
        ...     "U 8\\n"
        ...     "L 8\\n"
        ...     "D 3\\n"
        ...     "R 17\\n"
        ...     "D 10\\n"
        ...     "L 25\\n"
        ...     "U 20"
        ... )).tail_history_length
        36
        """
        return len(self.tail_history)

    def move_on_instructions(self, instructions: "InstructionSet") -> "LongRope":
        """
        >>> print(str(LongRope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 4\\n"
        ...     "U 4\\n"
        ...     "L 3\\n"
        ...     "D 1\\n"
        ...     "R 4\\n"
        ...     "D 1\\n"
        ...     "L 5\\n"
        ...     "R 2"
        ... ))))
        .1H3
        .5..
        6...
        >>> print(LongRope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 4\\n"
        ...     "U 4\\n"
        ...     "L 3\\n"
        ...     "D 1\\n"
        ...     "R 4\\n"
        ...     "D 1\\n"
        ...     "L 5\\n"
        ...     "R 2"
        ... )).get_history_diagram())
        s
        >>> print(str(LongRope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 5\\n"
        ...     "U 8\\n"
        ...     "L 8\\n"
        ...     "D 3\\n"
        ...     "R 17\\n"
        ...     "D 10\\n"
        ...     "L 25\\n"
        ...     "U 20"
        ... ))))
        H...........
        1...........
        2...........
        3...........
        4...........
        5...........
        6...........
        7...........
        8...........
        9...........
        ............
        ............
        ............
        ............
        ............
        ...........s

        >>> print(LongRope().move_on_instructions(InstructionSet.from_instructions_text(
        ...     "R 5\\n"
        ...     "U 8\\n"
        ...     "L 8\\n"
        ...     "D 3\\n"
        ...     "R 17\\n"
        ...     "D 10\\n"
        ...     "L 25\\n"
        ...     "U 20"
        ... )).get_history_diagram())
        #.....................
        #.............###.....
        #............#...#....
        .#..........#.....#...
        ..#..........#.....#..
        ...#........#.......#.
        ....#......s.........#
        .....#..............#.
        ......#............#..
        .......#..........#...
        ........#........#....
        .........########.....
        """
        for instruction in instructions.instructions:
            self.move(instruction.direction, instruction.amount)
        return self

    def move_on_instruction(self, instruction: "Instruction") -> "LongRope":
        return self.move(instruction.direction, instruction.amount)

    def move(self, direction: "Direction", amount: int) -> "LongRope":
        """
        >>> print(str(LongRope().move(Direction.Right, 1)))
        1H
        >>> print(str(LongRope().move(Direction.Right, 1).move(Direction.Right, 1)))
        21H
        >>> LongRope().move(Direction.Right, 1).move(Direction.Right, 1).move(Direction.Right,1 )
        LongRope(head=Point2D(x=3, y=0), tails=[Point2D(x=2, y=0), Point2D(x=1, y=0), Point2D(x=0, y=0), ...], tail_history={...})
        >>> print(str(LongRope().move(Direction.Right, 1).move(Direction.Right, 1).move(Direction.Right,1 )))
        321H
        >>> print(str(LongRope().move(Direction.Right, 2)))
        21H
        >>> print(str(LongRope().move(Direction.Right, 3)))
        321H
        >>> print(str(LongRope().move(Direction.Right, 1).move(Direction.Down, 1)))
        1.
        .H
        >>> print(str(LongRope().move(Direction.Right, 1).move(Direction.Down, 1).move(Direction.Right, 1)))
        2..
        .1H
        """
        for _ in range(amount):
            self.head = self.head.offset(direction.offset)
            for index in range(len(self.tails)):
                self.move_tail(index)
            self.tail_history.add(self.tails[-1])

        return self

    def move_tail(self, index: int) -> "LongRope":
        if index == 0:
            head = self.head
        else:
            head = self.tails[index - 1]
        tail = self.tails[index]
        gap = head.difference(tail)
        self.tails[index] = tail.offset(self.gap_move[gap])

        return self

    def __str__(self) -> str:
        """
        >>> print(str(LongRope()))
        H
        >>> print(str(LongRope(head=Point2D(1, 0))))
        1H
        """
        start = Point2D.get_zero_point()
        points = [start, self.head] + self.tails
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(points)
        return "\n".join(
            "".join(
                "H"
                if point == self.head else
                str(self.tails.index(point) + 1)
                if point in self.tails else
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


LongRope.gap_move = {
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


Challenge.main()
challenge = Challenge()
