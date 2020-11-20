#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Optional, Set, Tuple, Iterable

from utils import BaseChallenge, Point2D
from year_2016.day_01 import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        111
        """
        return WalkerExtended.get_first_duplicate_from_text(_input)\
            .manhattan_length()


@dataclass
class WalkerExtended(part_a.Walker['InstructionSetExtended']):
    history: Set[Point2D] = field(default_factory=set)
    duplicates: Set[Point2D] = field(default_factory=set)

    @classmethod
    def get_first_duplicate_from_text(cls, instructions_text: str) \
            -> Optional[Point2D]:
        """
        >>> WalkerExtended.get_first_duplicate_from_text('R2, L3')
        >>> WalkerExtended.get_first_duplicate_from_text('R2, R2, R2')
        >>> WalkerExtended.get_first_duplicate_from_text('R5, L5, R5, R3')
        >>> WalkerExtended.get_first_duplicate_from_text('R8, R4, R4, R8')
        Point2D(x=4, y=0)
        >>> WalkerExtended.get_first_duplicate_from_text('R8, R4, R4, R8')\\
        ...     .manhattan_length()
        4
        """
        instruction_set = cls.get_instruction_set_class()\
            .from_instructions_text(instructions_text)
        return cls().get_first_duplicate(instruction_set)

    def __post_init__(self):
        self.history.add(self.position)

    def get_first_duplicate(
            self, instruction_set: 'InstructionSetExtended') \
            -> Optional[Point2D]:
        """
        >>> WalkerExtended(Point2D(2, 3), part_a.Instruction.Direction.Right)\\
        ...     .get_first_duplicate(InstructionSetExtended([
        ...         InstructionExtended(InstructionExtended.Turn.Right, 10),
        ...         InstructionExtended(InstructionExtended.Turn.Left, 10),
        ...     ]))
        >>> WalkerExtended(Point2D(2, 3), InstructionExtended.Direction.Right)\\
        ...     .get_first_duplicate(InstructionSetExtended([
        ...         InstructionExtended(InstructionExtended.Turn.Right, 10),
        ...         InstructionExtended(InstructionExtended.Turn.Right, 0),
        ...         InstructionExtended(InstructionExtended.Turn.Right, 10),
        ...     ]))
        Point2D(x=2, y=12)
        """
        cls = type(self)
        # noinspection PyArgumentList
        other_walker = \
            cls(self.position, self.direction, {self.position}, set())
        other_walker.move(instruction_set, stop_on_duplicate=True)
        if not other_walker.duplicates:
            return None

        duplicate, = other_walker.duplicates
        return duplicate

    def move(self, instruction_set: 'InstructionSetExtended',
             stop_on_duplicate: bool = False):
        """
        >>> walker = WalkerExtended(Point2D(2, 3), InstructionExtended.Direction.Right)\\
        ...     .move(InstructionSetExtended([
        ...         InstructionExtended(InstructionExtended.Turn.Right, 2),
        ...         InstructionExtended(InstructionExtended.Turn.Right, 0),
        ...         InstructionExtended(InstructionExtended.Turn.Left, 2),
        ...     ]), stop_on_duplicate=True)
        >>> walker
        WalkerExtended(position=Point2D(x=2, y=7),
            direction=Direction.Down, history={...},
            duplicates=set())
        >>> sorted(walker.history)
        [Point2D(x=2, y=3), Point2D(x=2, y=4), Point2D(x=2, y=5),
            Point2D(x=2, y=6), Point2D(x=2, y=7)]
        >>> walker = WalkerExtended(Point2D(2, 3), InstructionExtended.Direction.Right)\\
        ...     .move(InstructionSetExtended([
        ...         InstructionExtended(InstructionExtended.Turn.Right, 2),
        ...         InstructionExtended(InstructionExtended.Turn.Right, 0),
        ...         InstructionExtended(InstructionExtended.Turn.Right, 2),
        ...     ]), stop_on_duplicate=True)
        >>> walker
        WalkerExtended(position=Point2D(x=2, y=4),
            direction=Direction.Up, history={...},
            duplicates={Point2D(x=2, y=4)})
        >>> sorted(walker.history)
        [Point2D(x=2, y=3), Point2D(x=2, y=4), Point2D(x=2, y=5)]
        """
        for position, direction \
                in instruction_set.get_moves(self.position, self.direction):
            if position is None:
                self.direction = direction
            else:
                self.position, self.direction = position, direction
                if self.add_position(self.position):
                    break

        return self

    def add_position(self, position: Point2D) -> bool:
        if position in self.history:
            self.duplicates.add(position)
            return True
        else:
            self.history.add(position)
            return False


class InstructionSetExtended(part_a.InstructionSet['InstructionExtended']):
    def get_moves(
            self, position: Point2D, direction: part_a.Instruction.Direction
    ) -> Iterable[Tuple[Optional[Point2D], part_a.Instruction.Direction]]:
        """
        >>> list(InstructionSetExtended([
        ...     InstructionExtended(InstructionExtended.Turn.Right, 2),
        ...     InstructionExtended(InstructionExtended.Turn.Right, 0),
        ...     InstructionExtended(InstructionExtended.Turn.Left, 2),
        ... ]).get_moves(Point2D(2, 3), InstructionExtended.Direction.Right))
        [(Point2D(x=2, y=4), Direction.Down),
            (Point2D(x=2, y=5), Direction.Down),
            (None, Direction.Left),
            ...]
        """
        for instruction in self.instructions:
            for new_position, new_direction \
                    in instruction.get_moves(position, direction):
                yield new_position, new_direction
                if new_position is None:
                    direction = new_direction
                else:
                    position, direction = new_position, new_direction


class InstructionExtended(part_a.Instruction):
    def get_moves(
            self, position: Point2D, direction: part_a.Instruction.Direction
    ) -> Iterable[Tuple[Optional[Point2D], part_a.Instruction.Direction]]:
        """
        >>> list(InstructionExtended(
        ...     InstructionExtended.Turn.Left, 10).get_moves(
        ...         Point2D(2, 3), InstructionExtended.Direction.Up))
        [(Point2D(x=1, y=3), Direction.Left),
            (Point2D(x=0, y=3), Direction.Left),
            ...,
            (Point2D(x=-7, y=3), Direction.Left),
            (Point2D(x=-8, y=3), Direction.Left)]
        >>> list(InstructionExtended(
        ...     InstructionExtended.Turn.Left, 10).get_moves(
        ...         Point2D(2, 3), InstructionExtended.Direction.Down))
        [(Point2D(x=3, y=3), Direction.Right),
            (Point2D(x=4, y=3), Direction.Right),
            ...,
            (Point2D(x=11, y=3), Direction.Right),
            (Point2D(x=12, y=3), Direction.Right)]
        >>> list(InstructionExtended(
        ...     InstructionExtended.Turn.Right, 10).get_moves(
        ...         Point2D(2, 3), InstructionExtended.Direction.Left))
        [(Point2D(x=2, y=2), Direction.Up),
            (Point2D(x=2, y=1), Direction.Up),
            ...,
            (Point2D(x=2, y=-6), Direction.Up),
            (Point2D(x=2, y=-7), Direction.Up)]
        >>> list(InstructionExtended(
        ...     InstructionExtended.Turn.Right, 10).get_moves(
        ...         Point2D(2, 3), InstructionExtended.Direction.Right))
        [(Point2D(x=2, y=4), Direction.Down),
            (Point2D(x=2, y=5), Direction.Down),
            ...,
            (Point2D(x=2, y=12), Direction.Down),
            (Point2D(x=2, y=13), Direction.Down)]
        >>> list(InstructionExtended(
        ...     InstructionExtended.Turn.Right, 0).get_moves(
        ...         Point2D(2, 5), InstructionExtended.Direction.Down))
        [(None, Direction.Left)]
        """
        direction_index = self.LEFT_ROTATION.index(direction)
        if self.turn == self.Turn.Left:
            direction_index += 1
        else:
            direction_index -= 1
        final_direction = \
            self.LEFT_ROTATION[direction_index % len(self.LEFT_ROTATION)]
        if not self.move_amount:
            yield None, final_direction
        else:
            for move_amount in range(1, self.move_amount + 1):
                position = position.offset(self.OFFSETS[final_direction])
                yield position, final_direction


Challenge.main()
challenge = Challenge()
