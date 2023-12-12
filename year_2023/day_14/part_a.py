#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Set, Union, Dict, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        111339
        """
        return Dish.from_map(_input).tilt_north().get_load_factor()


@dataclass
class Dish:
    rounded_rocks: Set[Point2D]
    square_rocks: Set[Point2D]
    width: int
    height: int

    @classmethod
    def from_map(cls, text: str) -> "Dish":
        """
        >>> print(Dish.from_map('''
        ...     O....#....
        ...     O.OO#....#
        ...     .....##...
        ...     OO.#O....O
        ...     .O.....O#.
        ...     O.#..O.#.#
        ...     ..O..#O..O
        ...     .......O..
        ...     #....###..
        ...     #OO..#....
        ... '''))
        O....#....
        O.OO#....#
        .....##...
        OO.#O....O
        .O.....O#.
        O.#..O.#.#
        ..O..#O..O
        .......O..
        #....###..
        #OO..#....
        """
        lines = list(map(str.strip, text.strip().splitlines()))
        rounded_rocks = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char == "O"
        }
        square_rocks = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char == "#"
        }
        width = len(lines[0]) if lines else 0
        height = len(lines)
        return cls(
            rounded_rocks=rounded_rocks,
            square_rocks=square_rocks,
            width=width, height=height,
        )

    def __str__(self) -> str:
        return "\n".join(
            "".join(
                "O"
                if point in self.rounded_rocks else
                "#"
                if point in self.square_rocks else
                "."
                for x in range(self.width)
                for point in [Point2D(x, y)]
            )
            for y in range(self.height)
        )

    def get_load_factor(self) -> int:
        """
        >>> Dish.from_map('''
        ...     OOOO.#.O..
        ...     OO..#....#
        ...     OO..O##..O
        ...     O..#.OO...
        ...     ........#.
        ...     ..#....#.#
        ...     ..O..#.O.O
        ...     ..O.......
        ...     #....###..
        ...     #....#....
        ... ''').get_load_factor()
        136
        """
        return sum(
            self.height - point.y
            for point in self.rounded_rocks
        )

    def tilt_north(self, cache: Optional[Dict[Point2D, Point2D]] = None) -> "Dish":
        """
        >>> print(Dish.from_map('''
        ...     O....#....
        ...     O.OO#....#
        ...     .....##...
        ...     OO.#O....O
        ...     .O.....O#.
        ...     O.#..O.#.#
        ...     ..O..#O..O
        ...     .......O..
        ...     #....###..
        ...     #OO..#....
        ... ''').tilt_north())
        OOOO.#.O..
        OO..#....#
        OO..O##..O
        O..#.OO...
        ........#.
        ..#....#.#
        ..O..#.O.O
        ..O.......
        #....###..
        #....#....
        """
        rounded_count_per_square: Dict[Point2D, int] = {}
        if cache is None:
            cache = {}
        for rounded in self.rounded_rocks:
            for y in range(rounded.y, -1, -1):
                point = Point2D(rounded.x, y)
                if point in cache:
                    target = cache[point]
                    rounded_count_per_square.setdefault(target, 0)
                    rounded_count_per_square[target] += 1
                    for y2 in range(point.y + 1, rounded.y + 1):
                        cache[Point2D(point.x, y2)] = target
                    break
                elif point in self.square_rocks:
                    rounded_count_per_square.setdefault(point, 0)
                    rounded_count_per_square[point] += 1
                    for y2 in range(point.y + 1, rounded.y + 1):
                        cache[Point2D(point.x, y2)] = point
                    break
            else:
                point = Point2D(rounded.x, -1)
                rounded_count_per_square.setdefault(point, 0)
                rounded_count_per_square[point] += 1
        new_rounded_rocks = set()
        for square, count in rounded_count_per_square.items():
            for y in range(square.y + 1, square.y + count + 1):
                new_rounded_rocks.add(Point2D(square.x, y))
        cls = type(self)
        return cls(
            rounded_rocks=new_rounded_rocks,
            square_rocks=self.square_rocks,
            width=self.width, height=self.height,
        )


Challenge.main()
challenge = Challenge()
