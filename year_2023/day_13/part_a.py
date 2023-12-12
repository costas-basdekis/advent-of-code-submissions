#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        37381
        """
        return MirrorValleySet.from_map(_input).summarize()


@dataclass
class MirrorValleySet:
    valleys: List["MirrorValley"]

    @classmethod
    def from_map(cls, text: str) -> "MirrorValleySet":
        """
        >>> print(MirrorValleySet.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ...
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... '''))
        #.##..##.
        ..#.##.#.
        ##......#
        ##......#
        ..#.##.#.
        ..##..##.
        #.#.##.#.
        <BLANKLINE>
        #...##..#
        #....#..#
        ..##..###
        #####.##.
        #####.##.
        ..##..###
        #....#..#
        """
        valleys = list(map(MirrorValley.from_map, text.strip().split("\n\n")))
        return cls(valleys=valleys)

    def __str__(self) -> str:
        return "\n\n".join(map(str, self.valleys))

    def summarize(self) -> int:
        """
        >>> MirrorValleySet.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ...
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''').summarize()
        405
        """
        return sum(
            (symmetry_index + 1) * (100 if is_vertical else 1)
            for valley in self.valleys
            for is_vertical, symmetry_index in [valley.get_symmetry_index()]
        )


@dataclass
class MirrorValley:
    rocks: Set[Point2D]
    width: int
    height: int

    @classmethod
    def from_map(cls, text: str) -> "MirrorValley":
        """
        >>> print(MirrorValley.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ... '''))
        #.##..##.
        ..#.##.#.
        ##......#
        ##......#
        ..#.##.#.
        ..##..##.
        #.#.##.#.
        """
        lines = text.strip().splitlines()
        rocks = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
            if char == "#"
        }
        width = len(lines[0]) if lines else 0
        height = len(lines)
        return cls(rocks=rocks, width=width, height=height)

    def get_symmetry_index(self) -> Tuple[bool, int]:
        """
        >>> MirrorValley.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ... ''').get_symmetry_index()
        (False, 4)
        >>> MirrorValley.from_map('''
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''').get_symmetry_index()
        (True, 3)
        """
        row_ids, column_ids = self.get_rows_and_columns_ids()
        row_index = self.get_last_mirror_index(row_ids)
        column_index = self.get_last_mirror_index(column_ids)
        if row_index != -1 and column_index != -1:
            raise Exception(f"Found both vertical ({row_index} in {row_ids}) and horizontal ({column_index} in {column_ids}) symmetry:\n{self}")
        if row_index == -1 and column_index == -1:
            raise Exception(f"No symmetry vertical ({row_ids}) or horizontal ({column_ids}) symmetry found:\n{self}")
        if row_index != -1:
            return True, row_index
        else:
            return False, column_index

    def get_last_mirror_index(self, ids: List[int]) -> int:
        """
        >>> MirrorValley(set(), 0, 0).get_last_mirror_index([0, 1, 2, 2, 1, 5, 6])
        -1
        >>> MirrorValley(set(), 0, 0).get_last_mirror_index([0, 1, 2, 3, 4, 4, 3, 2, 1])
        4
        >>> MirrorValley(set(), 0, 0).get_last_mirror_index([0, 1, 2, 3, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14])
        3
        """
        for last_index in range(len(ids)):
            first_list = ids[:last_index + 1]
            last_list = ids[last_index + 1:][::-1]
            if len(first_list) > len(last_list):
                first_list = first_list[-len(last_list):]
            elif len(first_list) < len(last_list):
                last_list = last_list[-len(first_list):]
            if first_list == last_list:
                return last_index
        return -1

    def get_rows_and_columns_ids(self) -> Tuple[List[int], List[int]]:
        """
        >>> _valley = MirrorValley.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ... ''')
        >>> _valley.get_rows_and_columns_ids()
        ([0, 1, 2, 2, 1, 5, 6], [0, 1, 2, 3, 4, 4, 3, 2, 1])
        """
        row_ids_by_contents = {}
        row_contents = [
            tuple(Point2D(x, y) in self.rocks for x in range(self.width))
            for y in range(self.height)
        ]
        for y in range(self.height):
            row_ids_by_contents.setdefault(row_contents[y], y)
        row_ids = [
            row_ids_by_contents[row_contents[y]]
            for y in range(self.height)
        ]
        column_ids_by_contents = {}
        column_contents = [
            tuple(Point2D(x, y) in self.rocks for y in range(self.height))
            for x in range(self.width)
        ]
        for x in range(self.width):
            column_ids_by_contents.setdefault(column_contents[x], x)
        column_ids = [
            column_ids_by_contents[column_contents[x]]
            for x in range(self.width)
        ]
        return row_ids, column_ids

    def __str__(self) -> str:
        return "\n".join(
            "".join(
                "#"
                if Point2D(x, y) in self.rocks else
                "."
                for x in range(self.width)
            )
            for y in range(self.height)
        )


Challenge.main()
challenge = Challenge()
