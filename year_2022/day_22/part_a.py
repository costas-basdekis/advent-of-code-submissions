#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass
import re
from enum import Enum
from typing import ClassVar, Dict, Iterable, List, Optional, Tuple, Union, Generic, Type

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Cls, min_and_max_tuples, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        30552
        """
        return PathFinder\
            .from_map_text(_input)\
            .get_password()


BoardT = TV["Board"]


@dataclass
class PathFinder(Generic[BoardT]):
    board: BoardT
    instructions: List["Instruction"]
    path: List[Tuple[Point2D, "Direction", str]]

    @classmethod
    def get_board_class(cls) -> Type[BoardT]:
        return get_type_argument_class(cls, BoardT)

    @classmethod
    def from_map_text(cls, map_text: str) -> "PathFinder":
        board_text, instructions_text = map_text.strip("\n").split("\n\n")
        board_class = cls.get_board_class()
        return cls(
            board=board_class.from_board_text(board_text),
            instructions=Instruction.parse_all(instructions_text),
            path=[],
        )

    def get_password(self) -> int:
        """
        >>> PathFinder.from_map_text(LONG_INPUT).get_password()
        6032
        """
        point, direction = self.traverse()
        return 1000 * (point.y + 1) + 4 * (point.x + 1) + direction.code

    def traverse(self) -> Tuple[Point2D, "Direction"]:
        """
        >>> PathFinder.from_map_text(LONG_INPUT).traverse()
        (Point2D(x=7, y=5), Direction.Right)
        """
        point = self.board.get_top_left_point()
        direction = Direction.Right
        for instruction in self.instructions:
            point, direction = instruction.advance(self.board, point, direction)
        return point, direction

    def trace_traverse(self) -> "PathFinder":
        """
        >>> finder = PathFinder.from_map_text(LONG_INPUT)
        >>> print(str(finder.trace_traverse()))
        :        >>v#
        :        .#v.
        :        #.v.
        :        ..v.
        :...#...v..v#
        :>>>v...>#.>>
        :..#v...#....
        :...>>>>v..#.
        :        ...#....
        :        .....#..
        :        .#......
        :        ......#.
        """
        point = self.board.get_top_left_point()
        direction = Direction.Right
        self.path = [(point, direction, "S")]
        for instruction in self.instructions:
            traversal = instruction.iterate_advance(
                self.board, point, direction,
            )
            for point, direction in traversal:
                self.path.append((point, direction, str(instruction)))
        return self

    def __str__(self, limit: Optional[int] = None) -> str:
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.board.points)
        path = self.path
        if limit is not None:
            path = path[:limit]
        direction_by_point = {
            point: direction
            for point, direction, _ in path
        }
        return "\n".join(
            ":{}".format(
                "".join(
                    str(direction)
                    if direction else
                    self.board.print_map[content]
                    for x in range(min_x, max_x + 1)
                    for point in [Point2D(x, y)]
                    for content in [self.board.points.get(point)]
                    for direction in [direction_by_point.get(point)]
                )
            )
            for y in range(min_y, max_y + 1)
        )

    def play(self):
        limit = 0
        while True:
            click.echo(click.style(f"Path: {limit}/{len(self.path)}", fg="green"))
            text = self.__str__(limit)
            if limit > 0:
                position, direction, instruction = self.path[limit - 1]
                if limit > 1:
                    previous_position, previous_direction, _ = self.path[limit - 2]
                    click.echo(click.style(
                        f"From {previous_position.x},{previous_position.y}/{previous_direction.name}, "
                        f"with Instruction: {instruction}, "
                        f"to {position.x},{position.y}/{direction.name}",
                        fg="green",
                    ))
                else:
                    click.echo(click.style(
                        f"With Instruction: {instruction}, "
                        f"at {position.x},{position.y}/{direction.name}",
                        fg="green",
                    ))
                lines = text.splitlines()
                lines[position.y] = "".join([
                    lines[position.y][:position.x + 1],
                    click.style(lines[position.y][position.x + 1], fg="green"),
                    lines[position.y][position.x + 2:],
                ])
                text = "\n".join(lines)
            click.echo(text)
            while True:
                click.echo(click.style(f"Path: {limit}/{len(self.path)}", fg="green"))
                if limit > 0:
                    position, direction, instruction = self.path[limit - 1]
                    if limit > 1:
                        previous_position, previous_direction, _ = self.path[limit - 2]
                        click.echo(click.style(
                            f"From {previous_position.x},{previous_position.y}/{previous_direction.name}, "
                            f"with Instruction: {instruction}, "
                            f"to {position.x},{position.y}/{direction.name}",
                            fg="green",
                        ))
                    else:
                        click.echo(click.style(
                            f"With Instruction: {instruction}, "
                            f"at {position.x},{position.y}/{direction.name}",
                            fg="green",
                        ))
                click.echo("Move forward (right), backwards (left), offset (O), position (P), exit (e)")
                char = click.getchar()
                if char == "\x1b[D":
                    limit -= 1
                    break
                elif char == "\x1b[C":
                    limit += 1
                    break
                elif char.lower() == "o":
                    offset = int(click.prompt(f"Input offset ({-limit} to {len(self.path) - limit})", type=int))
                    limit += offset
                    break
                elif char.lower() == "p":
                    limit = int(click.prompt(f"Input position (0 to {len(self.path)})", type=int))
                    break
                elif char.lower() == "e":
                    return
            limit = min(len(self.path), max(0, limit))


class Instruction(ABC):
    instruction_classes: ClassVar[List[Cls["Instruction"]]] = []

    @classmethod
    def parse_all(cls, instructions_text: str) -> "InstructionSet":
        """
        >>> Instruction.parse_all("10R5L5R10L4R5L5")
        [MoveInstruction(amount=10), RotateRightInstruction(), ...,
            RotateLeftInstruction(), MoveInstruction(amount=5)]
        """
        instructions = []
        remaining_text = instructions_text.strip()
        while remaining_text:
            instruction, remaining_text = cls.parse_portion(remaining_text)
            instructions.append(instruction)

        return instructions

    @classmethod
    def parse_portion(cls, text: str) -> Tuple["Instruction", str]:
        for instruction_cls in cls.instruction_classes:
            result = instruction_cls.try_parse_portion(text)
            if result:
                break
        else:
            raise Exception(f"Could not parse portion of '{text}'")
        return result

    @classmethod
    def try_parse_portion(
        cls, text: str,
    ) -> Optional[Tuple["Instruction", str]]:
        raise NotImplementedError()

    @classmethod
    def register(
        cls, instruction_cls: Cls["Instruction"],
    ) -> Cls["Instruction"]:
        cls.instruction_classes.append(instruction_cls)
        return instruction_cls

    def __str__(self) -> str:
        raise NotImplementedError()

    def advance(
        self, board: BoardT, point: Point2D, direction: "Direction",
    ) -> Tuple[Point2D, "Direction"]:
        for point, direction in self.iterate_advance(board, point, direction):
            pass
        return point, direction

    def iterate_advance(
        self, board: BoardT, point: Point2D, direction: "Direction",
    ) -> Iterable[Tuple[Point2D, "Direction"]]:
        raise NotImplementedError()


@Instruction.register
@dataclass
class MoveInstruction(Instruction):
    amount: int

    re_instruction = re.compile(r"^(\d+)")

    @classmethod
    def try_parse_portion(
        cls, text: str,
    ) -> Optional[Tuple["MoveInstruction", str]]:
        """
        >>> MoveInstruction.try_parse_portion("10R5L5R10L4R5L5")
        (MoveInstruction(amount=10), 'R5L5R10L4R5L5')
        """
        match = cls.re_instruction.match(text)
        if not match:
            return None
        amount_str, = match.groups()
        return cls(amount=int(amount_str)), text[len(amount_str):]

    def __str__(self) -> str:
        return f"{self.amount}"

    def iterate_advance(
        self, board: BoardT, point: Point2D, direction: "Direction",
    ) -> Iterable[Tuple[Point2D, "Direction"]]:
        """
        >>> instruction, _ = MoveInstruction.try_parse_portion("10")
        >>> _board = Board.from_board_text(BOARD_INPUT)
        >>> list(instruction.iterate_advance(
        ...     _board, Point2D(8, 0), Direction.Right))
        [(Point2D(x=9, y=0), Direction.Right),
            (Point2D(x=10, y=0), Direction.Right)]
        """
        for _ in range(self.amount):
            next_point, next_direction = board.get_next_point(point, direction)
            if board[next_point] == Content.Wall:
                break
            point, direction = next_point, next_direction
            yield point, next_direction


@Instruction.register
@dataclass
class RotateLeftInstruction(Instruction):
    re_instruction = re.compile(r"^L")

    @classmethod
    def try_parse_portion(
        cls, text: str,
    ) -> Optional[Tuple["RotateLeftInstruction", str]]:
        match = cls.re_instruction.match(text)
        if not match:
            return None
        instruction_str, = match.group()
        return cls(), text[len(instruction_str):]

    def __str__(self) -> str:
        return "L"

    def advance(
        self, board: BoardT, point: Point2D, direction: "Direction",
    ) -> Tuple[Point2D, "Direction"]:
        return point, direction.left

    def iterate_advance(
        self, board: BoardT, point: Point2D, direction: "Direction",
    ) -> Iterable[Tuple[Point2D, "Direction"]]:
        yield self.advance(board, point, direction)


@Instruction.register
@dataclass
class RotateRightInstruction(Instruction):
    re_instruction = re.compile(r"^R")

    @classmethod
    def try_parse_portion(
        cls, text: str,
    ) -> Optional[Tuple["RotateRightInstruction", str]]:
        match = cls.re_instruction.match(text)
        if not match:
            return None
        instruction_str, = match.group()
        return cls(), text[len(instruction_str):]

    def __str__(self) -> str:
        return "R"

    def iterate_advance(
        self, board: BoardT, point: Point2D, direction: "Direction",
    ) -> Iterable[Tuple[Point2D, "Direction"]]:
        yield point, direction.right


class Direction(Enum):
    Left = "left"
    Right = "right"
    Up = "up"
    Down = "down"

    offset_map: Dict["Direction", Point2D]
    opposite_map: Dict["Direction", "Direction"]
    left_map: Dict["Direction", "Direction"]
    right_map: Dict["Direction", "Direction"]
    code_map: Dict["Direction", int]
    print_map: Dict["Direction", str]

    @property
    def offset(self) -> Point2D:
        return self.offset_map[self]

    @property
    def opposite_offset(self) -> Point2D:
        return self.opposite.offset

    @property
    def opposite(self) -> "Direction":
        return self.opposite_map[self]

    @property
    def left(self) -> "Direction":
        return self.left_map[self]

    @property
    def right(self) -> "Direction":
        return self.right_map[self]

    @property
    def code(self) -> int:
        return self.code_map[self]

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __str__(self) -> str:
        return self.print_map[self]


Direction.offset_map = {
    Direction.Left: Point2D(-1, 0),
    Direction.Right: Point2D(1, 0),
    Direction.Up: Point2D(0, -1),
    Direction.Down: Point2D(0, 1),
}
Direction.opposite_map = {
    Direction.Left: Direction.Right,
    Direction.Right: Direction.Left,
    Direction.Up: Direction.Down,
    Direction.Down: Direction.Up,
}
Direction.left_map = {
    Direction.Left: Direction.Down,
    Direction.Right: Direction.Up,
    Direction.Up: Direction.Left,
    Direction.Down: Direction.Right,
}
Direction.right_map = {
    left: direction
    for direction, left in Direction.left_map.items()
}
Direction.code_map = {
    Direction.Right: 0,
    Direction.Down: 1,
    Direction.Left: 2,
    Direction.Up: 3,
}
Direction.print_map = {
    Direction.Left: "<",
    Direction.Right: ">",
    Direction.Up: "^",
    Direction.Down: "v",
}


class Content(Enum):
    Wall = "wall"
    Tile = "tile"


@dataclass
class Board:
    points: Dict[Point2D, Content]
    next_point_cache: Dict[Tuple[Point2D, Direction], Tuple[Point2D, Direction]]

    print_map: ClassVar[Dict[Optional[Content], str]] = {
        Content.Wall: "#",
        Content.Tile: ".",
        None: " ",
    }
    parse_map: ClassVar[Dict[str, Optional[Content]]] = {
        char: content
        for content, char in print_map.items()
    }

    @classmethod
    def from_board_text(cls, board_text: str) -> "Board":
        """
        >>> print(":" + str(Board.from_board_text(BOARD_INPUT)))
        :        ...#
                .#..
                #...
                ....
        ...#.......#
        ........#...
        ..#....#....
        ..........#.
                ...#....
                .....#..
                .#......
                ......#.
        """
        return cls(
            points={
                Point2D(x, y): content
                for y, line in enumerate(board_text.strip("\n").splitlines())
                for x, char in enumerate(line)
                for content in [cls.parse_map[char]]
                if content is not None
            },
            next_point_cache={},
        )

    def __str__(self) -> str:
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.points)
        return "\n".join(
            "".join(
                self.print_map[content]
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
                for content in [self.points.get(point)]
            )
            for y in range(min_y, max_y + 1)
        )

    def __getitem__(self, item: Point2D) -> Content:
        return self.points[item]

    def get_top_left_point(self) -> Point2D:
        """
        >>> Board.from_board_text(BOARD_INPUT).get_top_left_point()
        Point2D(x=8, y=0)
        """
        return min(
            self.points,
            key=lambda point: (point.y, point.x),
        )

    def get_next_point(self, point: Point2D, direction: Direction) -> Tuple[Point2D, Direction]:
        if point not in self.points:
            raise Exception(f"Point is not on board")
        if (point, direction) not in self.next_point_cache:
            next_point, next_direction = self.calculate_next_point(point, direction)
            if next_point not in self.points:
                raise Exception(f"Going from {(point, direction)} to {(next_point, next_direction)}: next point doesn't exist")
            self.next_point_cache[(point, direction)] = (next_point, next_direction)
            self.next_point_cache[(next_point, next_direction.opposite)] = (point, direction.opposite)
        return self.next_point_cache[(point, direction)]

    def calculate_next_point(self, point: Point2D, direction: Direction) -> Tuple[Point2D, Direction]:
        """
        >>> board = Board.from_board_text(BOARD_INPUT)
        >>> board.calculate_next_point(Point2D(8, 0), Direction.Right)
        (Point2D(x=9, y=0), Direction.Right)
        >>> board.calculate_next_point(Point2D(9, 0), Direction.Left)
        (Point2D(x=8, y=0), Direction.Left)
        >>> board.calculate_next_point(Point2D(8, 0), Direction.Down)
        (Point2D(x=8, y=1), Direction.Down)
        >>> board.calculate_next_point(Point2D(8, 1), Direction.Up)
        (Point2D(x=8, y=0), Direction.Up)
        >>> board.calculate_next_point(Point2D(8, 0), Direction.Left)
        (Point2D(x=11, y=0), Direction.Left)
        >>> board.calculate_next_point(Point2D(11, 0), Direction.Right)
        (Point2D(x=8, y=0), Direction.Right)
        >>> board.calculate_next_point(Point2D(8, 0), Direction.Up)
        (Point2D(x=8, y=11), Direction.Up)
        >>> board.calculate_next_point(Point2D(8, 11), Direction.Down)
        (Point2D(x=8, y=0), Direction.Down)
        """
        next_point = point.offset(direction.offset)
        if next_point in self.points:
            return next_point, direction

        return self.get_next_point_wrapped(point, direction)

    def get_next_point_wrapped(self, point: Point2D, direction: Direction) -> Tuple[Point2D, Direction]:
        opposite_offset = direction.opposite_offset
        next_point = point
        while True:
            next_next_point = next_point.offset(opposite_offset)
            if next_next_point not in self.points:
                break
            next_point = next_next_point
        return next_point, direction


Challenge.main()
challenge = Challenge()


LONG_INPUT = """
        ...#
        .#..
        #...
        ....
...#.......#
........#...
..#....#....
..........#.
        ...#....
        .....#..
        .#......
        ......#.

10R5L5R10L4R5L5
""".strip("\n")
BOARD_INPUT = LONG_INPUT.split("\n\n")[0]
INSTRUCTIONS_INPUT = LONG_INPUT.split("\n\n")[1]
