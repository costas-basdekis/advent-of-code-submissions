#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import List, Set, Tuple, Union

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Direction, min_and_max_tuples
from year_2024.day_15 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1437468
        """
        return DoubleWarehouse.from_warehouse_text(_input).apply_all_moves().get_gps_sum()

    def play(self):
        warehouse = DoubleWarehouse.from_warehouse_text('''
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

            <vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
            vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
            ><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
            <<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
            ^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
            ^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
            >^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
            <><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
            ^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
            v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
        ''')
        history = [warehouse]
        while True:
            next_direction = warehouse.directions[len(history) - 1] if len(history) <= len(warehouse.directions) else None
            if next_direction:
                print(str(warehouse).replace("@", str(next_direction)))
            else:
                print(warehouse)
            print(f"Moved {len(history) - 1}/{len(warehouse.directions)} times{', left for previous' if len(history) > 1 else ''}{', right for next' if next_direction else ''}, t to travel")
            while True:
                char = click.getchar()
                if char == "\x1b[C":
                    if not next_direction:
                        continue
                    warehouse = warehouse.copy().apply_move(next_direction)
                    history.append(warehouse)
                elif char == "\x1b[D":
                    if len(history) < 2:
                        continue
                    history.pop()
                    warehouse = history[-1]
                elif char == "t":
                    move_index = 0
                    while not (1 <= move_index <= len(warehouse.directions)):
                        move_index = click.prompt(f"Move index [0-{len(warehouse.directions)}]", type=int)
                    if move_index < len(history):
                        history = history[:move_index + 1]
                        warehouse = history[-1]
                    elif move_index >= len(history):
                        while move_index >= len(history):
                            warehouse = warehouse.copy().apply_move(warehouse.directions[len(history) - 1])
                            history.append(warehouse)
                else:
                    continue
                break


@dataclass
class DoubleWarehouse:
    walls: Set[Point2D]
    boxes: Set[Point2D]
    position: Point2D
    directions: List[Direction]

    @classmethod
    def from_warehouse_text(cls, text: str) -> "DoubleWarehouse":
        return cls.from_warehouse(part_a.Warehouse.from_text(text))

    @classmethod
    def from_warehouse(cls, warehouse: part_a.Warehouse) -> "DoubleWarehouse":
        """
        >>> print(DoubleWarehouse.from_warehouse_text('''
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
        ... '''))
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]....[]..[]##
        ##....[]@.....[]..##
        ##[]##....[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        """
        return cls(
            walls={
                double_wall
                for wall in warehouse.walls
                for double_wall in [Point2D(wall.x * 2, wall.y), Point2D(wall.x * 2 + 1, wall.y)]
            },
            boxes={
                double_box
                for box in warehouse.boxes
                for double_box in [Point2D(box.x * 2, box.y)]
            },
            position=Point2D(warehouse.position.x * 2, warehouse.position.y),
            directions=warehouse.directions,
        )

    @classmethod
    def from_text(cls, text: str) -> "DoubleWarehouse":
        """
        >>> print(DoubleWarehouse.from_text('''
        ...     ####################
        ...     ##....[]....[]..[]##
        ...     ##............[]..##
        ...     ##..[][]..[][]..[]##
        ...     ##...[]...[]..[]..##
        ...     ##[]##............##
        ...     ##[][]........[]..##
        ...     ##.........@[][][]##
        ...     ##[]......[]......##
        ...     ####################
        ...
        ...     ^
        ... '''))
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]..[][]..[]##
        ##...[]...[]..[]..##
        ##[]##............##
        ##[][]........[]..##
        ##.........@[][][]##
        ##[]......[]......##
        ####################
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
            if char == "["
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
                "["
                if position in self.boxes else
                "]"
                if position.offset(Point2D(-1, 0)) in self.boxes else
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

    def copy(self) -> "DoubleWarehouse":
        return DoubleWarehouse(
            walls=set(self.walls),
            boxes=set(self.boxes),
            position=self.position,
            directions=list(self.directions),
        )

    def get_gps_sum(self) -> int:
        """
        >>> DoubleWarehouse.from_warehouse_text('''
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
        9021
        """
        return sum(
            box.x + 100 * box.y
            for box in self.boxes
        )

    def apply_all_moves(self) -> "DoubleWarehouse":
        """
        >>> print(DoubleWarehouse.from_warehouse_text('''
        ...     #######
        ...     #...#.#
        ...     #.....#
        ...     #..OO@#
        ...     #..O..#
        ...     #.....#
        ...     #######
        ...
        ...     <vv<<^^<<^^
        ... ''').apply_all_moves())
        ##############
        ##...[].##..##
        ##...@.[]...##
        ##....[]....##
        ##..........##
        ##..........##
        ##############
        >>> print(DoubleWarehouse.from_warehouse_text('''
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
        ####################
        ##[].......[].[][]##
        ##[]...........[].##
        ##[]........[][][]##
        ##[]......[]....[]##
        ##..##......[]....##
        ##..[]............##
        ##..@......[].[][]##
        ##......[][]..[]..##
        ####################
        """
        for direction in self.directions:
            self.apply_move(direction)
        return self

    def apply_move(self, direction: Direction) -> "DoubleWarehouse":
        """
        >>> _warehouse = DoubleWarehouse.from_warehouse_text('''
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
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]....[]..[]##
        ##...[]@......[]..##
        ##[]##....[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        >>> print(_warehouse.copy().apply_move(Direction.Right))
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]....[]..[]##
        ##....[].@....[]..##
        ##[]##....[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        >>> print(_warehouse.copy().apply_move(Direction.Up))
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]@...[]..[]##
        ##....[]......[]..##
        ##[]##....[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        >>> print(_warehouse.copy().apply_move(Direction.Down))
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]....[]..[]##
        ##....[]......[]..##
        ##[]##..@.[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        >>> _warehouse = DoubleWarehouse.from_warehouse_text('''
        ...     ##########
        ...     #..O..O.O#
        ...     #......O.#
        ...     #@OO..O.O#
        ...     #..O...O.#
        ...     #O#..O...#
        ...     #O..O..O.#
        ...     #.OO.O.OO#
        ...     #....O...#
        ...     ##########
        ...
        ...     <
        ... ''')
        >>> print(_warehouse.apply_move(Direction.Right).apply_move(Direction.Right))
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..@[][]...[]..[]##
        ##....[]......[]..##
        ##[]##....[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        >>> _warehouse.position = Point2D(7, 5)
        >>> print(_warehouse)
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##...[][]...[]..[]##
        ##....[]......[]..##
        ##[]##.@..[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        >>> print(_warehouse.apply_move(Direction.Up))
        ####################
        ##....[]....[]..[]##
        ##...[][].....[]..##
        ##....[]....[]..[]##
        ##.....@......[]..##
        ##[]##....[]......##
        ##[]....[]....[]..##
        ##..[][]..[]..[][]##
        ##........[]......##
        ####################
        >>> print(DoubleWarehouse.from_text('''
        ...     ####################
        ...     ##....[]....[]..[]##
        ...     ##............[]..##
        ...     ##..[][]..[][]..[]##
        ...     ##...[]...[]..[]..##
        ...     ##[]##............##
        ...     ##[][]........[]..##
        ...     ##.........@[][][]##
        ...     ##[]......[]......##
        ...     ####################
        ...
        ...     ^
        ... ''').apply_move(Direction.Right))
        ####################
        ##....[]....[]..[]##
        ##............[]..##
        ##..[][]..[][]..[]##
        ##...[]...[]..[]..##
        ##[]##............##
        ##[][]........[]..##
        ##.........@[][][]##
        ##[]......[]......##
        ####################
        >>> print(DoubleWarehouse.from_text('''####################
        ...     ##....[]..[][][][]##
        ...     ##........[]....[]##
        ...     ##..[][]........[]##
        ...     ##...[]...........##
        ...     ##[]##.@..........##
        ...     ##[][]..........[]##
        ...     ##............[][]##
        ...     ##[]......[][][]..##
        ...     ####################
        ...
        ...     ^
        ... ''').apply_move(Direction.Left))
        ####################
        ##....[]..[][][][]##
        ##........[]....[]##
        ##..[][]........[]##
        ##...[]...........##
        ##[]##@...........##
        ##[][]..........[]##
        ##............[][]##
        ##[]......[][][]..##
        ####################
        """
        if direction == Direction.Left:
            self.apply_move_left()
        elif direction == Direction.Right:
            self.apply_move_right()
        else:
            self.apply_move_vertical(direction)
        return self

    def apply_move_left(self):
        direction = Direction.Left
        next_position = self.position.offset(direction.offset)
        if next_position in self.walls:
            return
        next_position_2 = self.position.offset(direction.offset, factor=2)
        if next_position_2 in self.walls:
            self.position = next_position
            return
        if next_position_2 not in self.boxes:
            self.position = next_position
            return
        boxes = set()
        while next_position_2 in self.boxes:
            boxes.add(next_position_2)
            next_position_2 = next_position_2.offset(direction.offset, factor=2)
        next_position = next_position_2.offset(direction.offset, factor=-1)
        if next_position in self.walls:
            return
        self.boxes -= boxes
        self.boxes |= {
            box.offset(direction.offset)
            for box in boxes
        }
        self.position = self.position.offset(direction.offset)

    def apply_move_right(self):
        direction = Direction.Right
        next_position = self.position.offset(direction.offset)
        if next_position in self.walls:
            return
        next_position_2 = next_position
        if next_position_2 not in self.boxes:
            self.position = next_position
            return
        boxes = set()
        while next_position_2 in self.boxes:
            boxes.add(next_position_2)
            next_position_2 = next_position_2.offset(direction.offset, factor=2)
        next_position = next_position_2
        if next_position in self.walls:
            return
        self.boxes -= boxes
        self.boxes |= {
            box.offset(direction.offset)
            for box in boxes
        }
        self.position = self.position.offset(direction.offset)

    def apply_move_vertical(self, direction: Direction):
        points = [self.position]
        boxes = set()
        while points:
            any_wall = any(
                point.offset(direction.offset) in self.walls
                for point in points
            )
            if any_wall:
                return
            next_boxes = {
                box
                for point in points
                for box in [point.offset(direction.offset), point.offset(direction.offset).offset(Point2D(-1, 0))]
                if box in self.boxes
            }
            next_points = {
                point
                for box in next_boxes
                for point in [box, box.offset(Point2D(1, 0))]
            }
            boxes |= next_boxes
            points = next_points
        if boxes:
            self.boxes -= boxes
            self.boxes |= {
                box.offset(direction.offset)
                for box in boxes
            }
        self.position = self.position.offset(direction.offset)

Challenge.main()
challenge = Challenge()
