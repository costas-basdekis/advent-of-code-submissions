#!/usr/bin/env python3
from typing import Iterable, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2023.day_16 import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        7324
        """
        return CaveExtended.from_map(_input).find_best_energization_level()


class CaveExtended(part_a.Cave):
    def find_best_energization_level(self) -> int:
        _, level = self.find_best_entry_point()
        return level

    def find_best_entry_point(self) -> Tuple[Tuple[Point2D, part_a.Direction], int]:
        """
        >>> CaveExtended.from_map('''
        ...     .|...*....
        ...     |.-.*.....
        ...     .....|-...
        ...     ........|.
        ...     ..........
        ...     .........*
        ...     ..../.**..
        ...     .-.-/..|..
        ...     .|....-|.*
        ...     ..//.|....
        ... ''').find_best_entry_point()
        ((Point2D(x=3, y=-1), Direction.Down), 51)
        """
        best_entry_point: Optional[Tuple[Tuple[Point2D, part_a.Direction], int]] = None
        for entry_point in self.get_possible_entry_points():
            energization_level = self.get_energization_level(entry_point=entry_point)
            if not best_entry_point or energization_level > best_entry_point[1]:
                best_entry_point = entry_point, energization_level
        if not best_entry_point:
            raise Exception(f"Could not find best entry point")
        return best_entry_point

    def get_possible_entry_points(self) -> Iterable[Tuple[Point2D, part_a.Direction]]:
        for x in range(self.width):
            yield Point2D(x, -1), part_a.Direction.Down
            yield Point2D(x, self.height), part_a.Direction.Up
        for y in range(self.height):
            yield Point2D(-1, y), part_a.Direction.Right
            yield Point2D(self.width, y), part_a.Direction.Left


Challenge.main()
challenge = Challenge()
