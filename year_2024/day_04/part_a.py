#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, Dict, Iterable, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples, Direction8


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return Puzzle.from_text(_input).get_all_xmas_direction_count()


@dataclass
class Puzzle:
    grid: Dict[Point2D, str]

    @classmethod
    def from_text(cls, text: str) -> "Puzzle":
        """
        >>> print(Puzzle.from_text('''
        ...     MMMSXXMASM
        ...     MSAMXMSMSA
        ...     AMXSXMAAMM
        ...     MSAMASMSMX
        ...     XMASAMXAMM
        ...     XXAMMXXAMA
        ...     SMSMSASXSS
        ...     SAXAMASAAA
        ...     MAMMMXMMMM
        ...     MXMXAXMASX
        ... '''))
        MMMSXXMASM
        MSAMXMSMSA
        AMXSXMAAMM
        MSAMASMSMX
        XMASAMXAMM
        XXAMMXXAMA
        SMSMSASXSS
        SAXAMASAAA
        MAMMMXMMMM
        MXMXAXMASX
        """
        return cls(grid={
            Point2D(x, y): char
            for y, line in enumerate(text.strip().splitlines())
            for x, char in enumerate(line.strip())
        })

    def __str__(self) -> str:
        return self.show()

    def show(self, only_points: Optional[Set[Point2D]] = None) -> str:
        if only_points is not None:
            if not only_points:
                return ""
            (min_x, min_y), (max_x, max_y) = min_and_max_tuples(only_points)
        else:
            (min_x, min_y), (max_x, max_y) = self.boundaries
        return "\n".join(
            "".join(
                self.grid[point]
                if only_points is None or point in only_points else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.grid)

    def get_points_with_xmas(self) -> Set[Point2D]:
        """
        >>> _puzzle = Puzzle.from_text('''
        ...     MMMSXXMASM
        ...     MSAMXMSMSA
        ...     AMXSXMAAMM
        ...     MSAMASMSMX
        ...     XMASAMXAMM
        ...     XXAMMXXAMA
        ...     SMSMSASXSS
        ...     SAXAMASAAA
        ...     MAMMMXMMMM
        ...     MXMXAXMASX
        ... ''')
        >>> _points = _puzzle.get_points_with_xmas()
        >>> len(_points)
        54
        >>> print("!" + _puzzle.show(_points))
        !....XXMAS.
        .SAMXMS...
        ...S..A...
        ..A.A.MS.X
        XMASAMX.MM
        X.....XA.A
        S.S.S.S.SS
        .A.A.A.A.A
        ..M.M.M.MM
        .X.X.XMASX
        """
        return {
            offset_point
            for point, direction in self.get_all_xmas_directions()
            for offset_point in self.get_xmas_points_at(point, direction)
        }

    def get_all_xmas_direction_count(self) -> int:
        """
        >>> Puzzle.from_text('''
        ...     MMMSXXMASM
        ...     MSAMXMSMSA
        ...     AMXSXMAAMM
        ...     MSAMASMSMX
        ...     XMASAMXAMM
        ...     XXAMMXXAMA
        ...     SMSMSASXSS
        ...     SAXAMASAAA
        ...     MAMMMXMMMM
        ...     MXMXAXMASX
        ... ''').get_all_xmas_direction_count()
        18
        """
        return sum(
            1
            for _ in self.get_all_xmas_directions()
        )

    def get_all_xmas_directions(self) -> Iterable[Tuple[Point2D, Direction8]]:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                point = Point2D(x, y)
                for direction in self.get_xmas_directions_at(point):
                    yield point, direction

    def get_xmas_directions_at(self, point: Point2D) -> Iterable[Direction8]:
        return (
            direction
            for direction in Direction8
            if self.is_xmas_at(point, direction)
        )

    xmas_offsets_by_direction: ClassVar[Dict[Direction8, List[Point2D]]] = {
        direction: [
            direction.offset.resize(factor=count)
            for count in range(4)
        ]
        for direction in Direction8
    }

    def is_xmas_at(self, point: Point2D, direction: Direction8) -> bool:
        """
        >>> Puzzle.from_text('''
        ...     MMMSXXMASM
        ...     MSAMXMSMSA
        ...     AMXSXMAAMM
        ...     MSAMASMSMX
        ...     XMASAMXAMM
        ...     XXAMMXXAMA
        ...     SMSMSASXSS
        ...     SAXAMASAAA
        ...     MAMMMXMMMM
        ...     MXMXAXMASX
        ... ''').is_xmas_at(Point2D(4, 0), Direction8.DownRight)
        True
        """
        return all(
            self.grid.get(point.offset(offset_point)) == char
            for char, offset_point in zip("XMAS", self.xmas_offsets_by_direction[direction])
        )

    def get_xmas_points_at(self, point: Point2D, direction: Direction8) -> List[Point2D]:
        return [
            point.offset(offset)
            for offset in self.xmas_offsets_by_direction[direction]
        ]


Challenge.main()
challenge = Challenge()
