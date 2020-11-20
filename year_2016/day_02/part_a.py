#!/usr/bin/env python3
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Union

from utils import BaseChallenge, Point2D
from utils.typing_utils import Cls, Self


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '92435'
        """
        instruction_lines = InstructionLine.from_lines_text(_input)
        return Numpad.standard_9_buttons().get_code(instruction_lines)


@dataclass
class Numpad:
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    button_by_position: Dict[Point2D, int]
    position_by_button: Dict[int, Point2D] = field(init=False)

    @classmethod
    def standard_9_buttons(cls):
        # noinspection PyArgumentList
        return cls(0, 2, 0, 2, {
            Point2D(0, 0): 1,
            Point2D(1, 0): 2,
            Point2D(2, 0): 3,
            Point2D(0, 1): 4,
            Point2D(1, 1): 5,
            Point2D(2, 1): 6,
            Point2D(0, 2): 7,
            Point2D(1, 2): 8,
            Point2D(2, 2): 9,
        })

    def __post_init__(self):
        self.initialise_position_by_button()

    def initialise_position_by_button(self):
        """
        >>> numpad = Numpad.standard_9_buttons()
        >>> # noinspection PyUnresolvedReferences
        >>> {
        ...     button: numpad.button_by_position[
        ...         numpad.position_by_button[button]]
        ...     for button in range(1, 10)
        ... }
        {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}
        """
        self.position_by_button = {
            button: position
            for position, button in self.button_by_position.items()
        }

    def get_code(self, instruction_lines: List['InstructionLine'],
                 start: int = 5) -> str:
        """
        >>> numpad = Numpad.standard_9_buttons()
        >>> numpad.get_code([])
        ''
        >>> numpad.get_code(InstructionLine.from_lines_text(
        ...     'ULL\\nRRDDD\\nLURDL\\nUUUUD'))
        '1985'
        """
        return "".join(map(str, self.get_button_sequence(instruction_lines)))

    def get_button_sequence(
            self, instruction_lines: List['InstructionLine'], start: int = 5,
    ) -> List[int]:
        """
        >>> numpad = Numpad.standard_9_buttons()
        >>> numpad.get_button_sequence([])
        []
        >>> numpad.get_button_sequence(InstructionLine.from_lines_text(
        ...     'ULL\\nRRDDD\\nLURDL\\nUUUUD'))
        [1, 9, 8, 5]
        """
        sequence = []
        position = start
        for instruction_line in instruction_lines:
            position = self.move_button(position, instruction_line)
            sequence.append(position)

        return sequence

    def move_button(self, start: int, instruction_line: 'InstructionLine'
                    ) -> int:
        """
        >>> numpad = Numpad.standard_9_buttons()
        >>> numpad.move_button(5, InstructionLine.from_line_text('ULL'))
        1
        >>> numpad.move_button(1, InstructionLine.from_line_text('RRDDD'))
        9
        >>> numpad.move_button(9, InstructionLine.from_line_text('LURDL'))
        8
        >>> numpad.move_button(8, InstructionLine.from_line_text('UUUUD'))
        5
        """
        start_position = self.position_by_button[start]
        end_position = instruction_line.move(
            start_position, self.min_x, self.max_x, self.min_y, self.max_y)
        return self.button_by_position[end_position]

    def show(self):
        """
        >>> print(Numpad.standard_9_buttons().show())
        1 2 3
        4 5 6
        7 8 9
        """
        # noinspection PyArgumentList
        return "\n".join(
            " ".join(
                str(self.button_by_position[Point2D(x, y)])
                for x in range(self.min_x, self.max_x + 1)
            )
            for y in range(self.min_y, self.max_y + 1)
        )


@dataclass
class InstructionLine:
    class Direction(Enum):
        Up = "U"
        Down = "D"
        Left = "L"
        Right = "R"

        def __repr__(self):
            return f"{type(self).__name__}.{self.name}"

    directions: List[Direction]

    # noinspection PyArgumentList
    DIRECTION_OFFSETS = {
        Direction.Up: Point2D(0, -1),
        Direction.Down: Point2D(0, 1),
        Direction.Left: Point2D(-1, 0),
        Direction.Right: Point2D(1, 0),
    }

    @classmethod
    def from_lines_text(cls: Cls['InstructionLine'], lines_text: str
                        ) -> List[Self['InstructionLine']]:
        """
        >>> InstructionLine.from_lines_text('ULL')
        [InstructionLine(directions=[Direction.Up,
            Direction.Left, Direction.Left])]
        >>> # noinspection PyUnresolvedReferences
        >>> "\\n".join(
        ...     instruction_line.show()
        ...     for instruction_line in InstructionLine.from_lines_text(
        ...         'ULL\\nRRDDD\\nLURDL\\nUUUUD')
        ... )
        'ULL\\nRRDDD\\nLURDL\\nUUUUD'
        """
        return list(map(cls.from_line_text, lines_text.strip().splitlines()))

    @classmethod
    def from_line_text(cls: Cls['InstructionLine'], line_text: str
                       ) -> Self['InstructionLine']:
        """
        >>> InstructionLine.from_line_text('ULL')
        InstructionLine(directions=[Direction.Up,
            Direction.Left, Direction.Left])
        """
        return cls(list(map(cls.Direction, line_text)))

    def move(self, position: Point2D, min_x: int, max_x: int, min_y: int,
             max_y: int) -> Point2D:
        """
        >>> InstructionLine.from_line_text('')\\
        ...     .move(Point2D(1, 1), 0, 2, 0, 2)
        Point2D(x=1, y=1)
        >>> InstructionLine.from_line_text('ULL')\\
        ...     .move(Point2D(1, 1), 0, 2, 0, 2)
        Point2D(x=0, y=0)
        >>> InstructionLine.from_line_text('UUUDDD')\\
        ...     .move(Point2D(1, 1), 0, 2, 0, 2)
        Point2D(x=1, y=2)
        >>> InstructionLine.from_line_text('ULL')\\
        ...     .move(Point2D(3, 3), 0, 6, 0, 6)
        Point2D(x=1, y=2)
        """
        for direction in self.directions:
            position = self.move_in_direction(
                position, direction, min_x, max_x, min_y, max_y)

        return position

    def move_in_direction(self, position: Point2D, direction: Direction,
                          min_x: int, max_x: int, min_y: int, max_y: int) \
            -> Point2D:
        """
        >>> InstructionLine([]).move_in_direction(
        ...     Point2D(1, 1), InstructionLine.Direction.Up, 0, 2, 0, 2)
        Point2D(x=1, y=0)
        >>> InstructionLine([]).move_in_direction(
        ...     Point2D(1, 0), InstructionLine.Direction.Up, 0, 2, 0, 2)
        Point2D(x=1, y=0)
        >>> InstructionLine([]).move_in_direction(
        ...     Point2D(1, 1), InstructionLine.Direction.Down, 0, 2, 0, 2)
        Point2D(x=1, y=2)
        >>> InstructionLine([]).move_in_direction(
        ...     Point2D(1, 2), InstructionLine.Direction.Down, 0, 2, 0, 2)
        Point2D(x=1, y=2)
        >>> InstructionLine([]).move_in_direction(
        ...     Point2D(1, 1), InstructionLine.Direction.Left, 0, 2, 0, 2)
        Point2D(x=0, y=1)
        >>> InstructionLine([]).move_in_direction(
        ...     Point2D(0, 1), InstructionLine.Direction.Left, 0, 2, 0, 2)
        Point2D(x=0, y=1)
        >>> InstructionLine([]).move_in_direction(
        ...     Point2D(1, 1), InstructionLine.Direction.Right, 0, 2, 0, 2)
        Point2D(x=2, y=1)
        >>> InstructionLine([]).move_in_direction(
        ...     Point2D(2, 1), InstructionLine.Direction.Right, 0, 2, 0, 2)
        Point2D(x=2, y=1)
        """
        x, y = position.offset(self.DIRECTION_OFFSETS[direction])
        if x < min_x:
            x = position.x
        elif x > max_x:
            x = position.x
        if y < min_y:
            y = position.y
        elif y > max_y:
            y = position.y

        # noinspection PyArgumentList
        return Point2D(x, y)

    def show(self):
        """
        >>> InstructionLine(directions=[
        ...     InstructionLine.Direction.Up, InstructionLine.Direction.Left,
        ...     InstructionLine.Direction.Left]).show()
        'ULL'
        """
        return "".join(direction.value for direction in self.directions)


Challenge.main()
challenge = Challenge()
