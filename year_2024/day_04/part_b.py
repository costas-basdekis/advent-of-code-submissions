#!/usr/bin/env python3
from typing import ClassVar, Iterable, List, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Direction8
from year_2024.day_04 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1873
        """
        return PuzzleExtended.from_text(_input).get_all_double_mas_position_count()


class PuzzleExtended(part_a.Puzzle):
    def get_points_with_double_mas(self) -> Set[Point2D]:
        """
        >>> _puzzle = PuzzleExtended.from_text('''
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
        >>> _points = _puzzle.get_points_with_double_mas()
        >>> print("!" + _puzzle.show(_points))
        !.M.S......
        ..A..MSMS.
        .M.S.MAA..
        ..A.ASMSM.
        .M.S.M....
        ..........
        S.S.S.S.S.
        .A.A.A.A..
        M.M.M.M.M.
        ..........
        """
        return {
            offset_point
            for point in self.get_all_double_mas_positions()
            for offset_points in [[point], self.get_double_mas_points_at(point)]
            for offset_point in offset_points
        }

    def get_all_double_mas_position_count(self) -> int:
        """
        >>> PuzzleExtended.from_text('''
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
        ... ''').get_all_double_mas_position_count()
        9
        """
        return sum(
            1
            for _ in self.get_all_double_mas_positions()
        )

    def get_all_double_mas_positions(self) -> Iterable[Point2D]:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                point = Point2D(x, y)
                if self.is_double_mas_at(point):
                    yield point

    double_mas_offsets: ClassVar[List[Point2D]] = [
        Direction8.UpLeft.offset,
        Direction8.DownRight.offset,
        Direction8.UpRight.offset,
        Direction8.DownLeft.offset,
    ]

    double_mas_patterns: ClassVar[Set[str]] = {
        "MSMS",
        "SMMS",
        "SMSM",
        "MSSM",
    }

    def is_double_mas_at(self, point: Point2D) -> bool:
        """
        >>> PuzzleExtended.from_text('''
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
        ... ''').is_double_mas_at(Point2D(2, 1))
        True
        """
        if self.grid.get(point) != "A":
            return False
        pattern = "".join(
            self.grid.get(offset_point, "")
            for offset_point in self.get_double_mas_points_at(point)
        )
        return pattern in self.double_mas_patterns

    def get_double_mas_points_at(self, point: Point2D) -> List[Point2D]:
        return [
            point.offset(offset)
            for offset in self.double_mas_offsets
        ]


Challenge.main()
challenge = Challenge()
