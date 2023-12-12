#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import List, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Cls, Self, Direction, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1437174
        """
        return Warehouse.from_text(_input).apply_all_moves().get_gps_sum()


@dataclass
class Warehouse:
    walls: Set[Point2D]
    boxes: Set[Point2D]
    position: Point2D
    directions: List[Direction]

    @classmethod
    def from_text(cls, text: str) -> "Warehouse":
        """
        >>> _warehouse = Warehouse.from_text('''
        ...     ##########
        ...     #..O..O.O#
        ...     #......O.#
        ...     #.OO..O.O#
        ...     #..O@..O.#
        ...     #O#..O...#
        ...     #O..O..O.#
        ...     #.OO.O.OO#
        ...     #....O...#
        ...     ##########
        ...
        ...     <vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
        ...     vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
        ...     ><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
        ...     <<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
        ...     ^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
        ...     ^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
        ...     >^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
        ...     <><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
        ...     ^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
        ...     v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
        ... ''')
        >>> print(_warehouse)
        ##########
        #..O..O.O#
        #......O.#
        #.OO..O.O#
        #..O@..O.#
        #O#..O...#
        #O..O..O.#
        #.OO.O.OO#
        #....O...#
        ##########
        >>> len(_warehouse.directions)
        700
        """
        warehouse_str, directions_str = text.strip().split("\n\n")
        warehouse_lines = warehouse_str.strip().splitlines()
        walls = {
            Point2D(x, y)
            for y, line in enumerate(warehouse_lines)
            for x, char in enumerate(line.strip())
            if char == "#"
        }
        boxes = {
            Point2D(x, y)
            for y, line in enumerate(warehouse_lines)
            for x, char in enumerate(line.strip())
            if char == "O"
        }
        position, = {
            Point2D(x, y)
            for y, line in enumerate(warehouse_lines)
            for x, char in enumerate(line.strip())
            if char == "@"
        }
        directions = list(map(Direction.parse, directions_str.strip().replace("\n", "").replace(" ", "")))
        return cls(walls=walls, boxes=boxes, position=position, directions=directions)

    def __str__(self) -> str:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return "\n".join(
            "".join(
                "@"
                if position == self.position else
                "O"
                if position in self.boxes else
                "#"
                if position in self.walls else
                "."
                for x in range(min_x, max_x + 1)
                for position in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.walls)

    def copy(self: Self["Warehouse"]) -> Cls["Warehouse"]:
        cls = type(self)
        return cls(
            walls=set(self.walls),
            boxes=set(self.boxes),
            position=self.position,
            directions=list(self.directions),
        )

    def get_gps_sum(self) -> int:
        """
        >>> Warehouse.from_text('''
        ...     ########
        ...     #..O.O.#
        ...     ##@.O..#
        ...     #...O..#
        ...     #.#.O..#
        ...     #...O..#
        ...     #......#
        ...     ########
        ...
        ...     <^^>>>vv<v>>v<<
        ... ''').apply_all_moves().get_gps_sum()
        2028
        >>> Warehouse.from_text('''
        ...     ##########
        ...     #..O..O.O#
        ...     #......O.#
        ...     #.OO..O.O#
        ...     #..O@..O.#
        ...     #O#..O...#
        ...     #O..O..O.#
        ...     #.OO.O.OO#
        ...     #....O...#
        ...     ##########
        ...
        ...     <vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
        ...     vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
        ...     ><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
        ...     <<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
        ...     ^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
        ...     ^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
        ...     >^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
        ...     <><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
        ...     ^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
        ...     v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
        ... ''').apply_all_moves().get_gps_sum()
        10092
        """
        return sum(
            box.x + 100 * box.y
            for box in self.boxes
        )

    def apply_all_moves(self: Self["Warehouse"]) -> Self["Warehouse"]:
        """
        >>> print(Warehouse.from_text('''
        ...     ########
        ...     #..O.O.#
        ...     ##@.O..#
        ...     #...O..#
        ...     #.#.O..#
        ...     #...O..#
        ...     #......#
        ...     ########
        ...
        ...     <^^>>>vv<v>>v<<
        ... ''').apply_all_moves())
        ########
        #....OO#
        ##.....#
        #.....O#
        #.#O@..#
        #...O..#
        #...O..#
        ########
        >>> print(Warehouse.from_text('''
        ...     ##########
        ...     #..O..O.O#
        ...     #......O.#
        ...     #.OO..O.O#
        ...     #..O@..O.#
        ...     #O#..O...#
        ...     #O..O..O.#
        ...     #.OO.O.OO#
        ...     #....O...#
        ...     ##########
        ...
        ...     <vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
        ...     vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
        ...     ><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
        ...     <<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
        ...     ^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
        ...     ^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
        ...     >^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
        ...     <><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
        ...     ^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
        ...     v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
        ... ''').apply_all_moves())
        ##########
        #.O.O.OOO#
        #........#
        #OO......#
        #OO@.....#
        #O#.....O#
        #O.....OO#
        #O.....OO#
        #OO....OO#
        ##########
        """
        for direction in self.directions:
            self.apply_move(direction)
        return self

    def apply_move(self: Self["Warehouse"], direction: Direction) -> Self["Warehouse"]:
        """
        >>> _warehouse = Warehouse.from_text('''
        ...     ##########
        ...     #..O..O.O#
        ...     #......O.#
        ...     #.OO..O.O#
        ...     #..O@..O.#
        ...     #O#..O...#
        ...     #O..O..O.#
        ...     #.OO.O.OO#
        ...     #....O...#
        ...     ##########
        ...
        ...     <
        ... ''')
        >>> print(_warehouse.copy().apply_move(Direction.Left))
        ##########
        #..O..O.O#
        #......O.#
        #.OO..O.O#
        #.O@...O.#
        #O#..O...#
        #O..O..O.#
        #.OO.O.OO#
        #....O...#
        ##########
        >>> print(_warehouse.copy().apply_move(Direction.Right))
        ##########
        #..O..O.O#
        #......O.#
        #.OO..O.O#
        #..O.@.O.#
        #O#..O...#
        #O..O..O.#
        #.OO.O.OO#
        #....O...#
        ##########
        >>> print(_warehouse.copy().apply_move(Direction.Up))
        ##########
        #..O..O.O#
        #......O.#
        #.OO@.O.O#
        #..O...O.#
        #O#..O...#
        #O..O..O.#
        #.OO.O.OO#
        #....O...#
        ##########
        >>> print(_warehouse.copy().apply_move(Direction.Down))
        ##########
        #..O..O.O#
        #......O.#
        #.OO..O.O#
        #..O...O.#
        #O#.@O...#
        #O..O..O.#
        #.OO.O.OO#
        #....O...#
        ##########
        """
        next_position = self.position.offset(direction.offset)
        if next_position in self.walls:
            return self
        if next_position not in self.boxes:
            self.position = next_position
            return self
        first_box_position = next_position
        box_count = 0
        while next_position in self.boxes:
            box_count += 1
            next_position = next_position.offset(direction.offset)
        if next_position in self.walls:
            return self
        first_empty_position = next_position
        self.boxes.remove(first_box_position)
        self.boxes.add(first_empty_position)
        self.position = first_box_position
        return self


Challenge.main()
challenge = Challenge()
