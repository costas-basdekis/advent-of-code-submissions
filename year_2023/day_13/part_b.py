#!/usr/bin/env python3
from typing import List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2023.day_13 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        28210
        """
        return MirrorValleySetExtended.from_map(_input).summarize_smudges()


class MirrorValleySetExtended(part_a.MirrorValleySet["MirrorValleyExtended"]):
    def summarize_smudges(self) -> int:
        """
        >>> MirrorValleySetExtended.from_map('''
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
        ... ''').summarize_smudges()
        400
        """
        return sum(
            (symmetry_index + 1) * (100 if is_vertical else 1)
            for valley in self.valleys
            for is_vertical, symmetry_index in [valley.get_smudge_symmetry_index()]
        )


class MirrorValleyExtended(part_a.MirrorValley):
    def get_smudge_symmetry_index(self) -> Tuple[bool, int]:
        """
        >>> MirrorValleyExtended.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ... ''').get_smudge_symmetry_index()
        (True, 2)
        >>> MirrorValleyExtended.from_map('''
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''').get_smudge_symmetry_index()
        (True, 0)
        >>> MirrorValleyExtended.from_map('''
        ...     .#.##.#.##..###
        ...     ...##...#######
        ...     #.####.#.#.###.
        ...     #..##..##..#...
        ...     ###..###....###
        ...     .##..##..#.#...
        ...     .#....#..######
        ...     #..##..########
        ...     ########.#..#..
        ... ''').get_smudge_symmetry_index()
        (False, 13)
        """
        _, is_vertical, symmetry_index = self.find_smudge()
        return is_vertical, symmetry_index

    def find_smudge(self) -> Tuple[Point2D, bool, int]:
        """
        >>> MirrorValleyExtended.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ... ''').find_smudge()
        (Point2D(x=0, y=0), True, 2)
        >>> MirrorValleyExtended.from_map('''
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''').find_smudge()
        (Point2D(x=4, y=0), True, 0)
        """
        symmetry_index_sets = self.get_symmetry_index_sets()
        for x in range(self.width):
            for y in range(self.height):
                point = Point2D(x, y)
                is_smudge, is_vertical, symmetry_index = self.is_point_a_smudge(point, symmetry_index_sets)
                if not is_smudge:
                    continue
                return point, is_vertical, symmetry_index
        raise Exception(f"Could not find smudge:\n{self}")

    def is_point_a_smudge(self, point: Point2D, symmetry_index_sets: Optional[Tuple[List[int], List[int]]] = None) -> Tuple[bool, bool, int]:
        """
        >>> _valley = MirrorValleyExtended.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ... ''')
        >>> _valley.is_point_a_smudge(Point2D(0, 0))
        (True, True, 2)
        >>> _valley.is_point_a_smudge(Point2D(1, 1))
        (False, False, -1)
        >>> _valley = MirrorValleyExtended.from_map('''
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''')
        >>> _valley.is_point_a_smudge(Point2D(4, 0))
        (True, True, 0)
        >>> _valley.is_point_a_smudge(Point2D(4, 1))
        (True, True, 0)
        """
        if symmetry_index_sets is None:
            symmetry_index_sets = self.get_symmetry_index_sets()
        row_index_set, column_index_set = symmetry_index_sets
        new_row_index_set, new_column_index_set = self.fix_point(point).get_symmetry_index_sets()
        if [] != new_row_index_set != row_index_set:
            return True, True, list(set(new_row_index_set) - set(row_index_set))[0]
        elif [] != new_column_index_set != column_index_set:
            return True, False, list(set(new_column_index_set) - set(column_index_set))[0]
        return False, False, -1

    def fix_point(self, point: Point2D) -> "MirrorValleyExtended":
        """
        >>> print(MirrorValleyExtended.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ... ''').fix_point(Point2D(0, 0)))
        ..##..##.
        ..#.##.#.
        ##......#
        ##......#
        ..#.##.#.
        ..##..##.
        #.#.##.#.
        >>> print(MirrorValleyExtended.from_map('''
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''').fix_point(Point2D(4, 1)))
        #...##..#
        #...##..#
        ..##..###
        #####.##.
        #####.##.
        ..##..###
        #....#..#
        """
        cls = type(self)
        if point in self.rocks:
            return cls(rocks=self.rocks - {point}, width=self.width, height=self.height)
        else:
            return cls(rocks=self.rocks | {point}, width=self.width, height=self.height)

    def get_symmetry_index_sets(self) -> Tuple[List[int], List[int]]:
        """
        >>> MirrorValleyExtended.from_map('''
        ...     #.##..##.
        ...     ..#.##.#.
        ...     ##......#
        ...     ##......#
        ...     ..#.##.#.
        ...     ..##..##.
        ...     #.#.##.#.
        ... ''').get_symmetry_index_sets()
        ([], [4])
        >>> MirrorValleyExtended.from_map('''
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''').get_symmetry_index_sets()
        ([3], [])
        >>> MirrorValleyExtended.from_map('''
        ...     #...##..#
        ...     #....#..#
        ...     ..##..###
        ...     #####.##.
        ...     #####.##.
        ...     ..##..###
        ...     #....#..#
        ... ''').fix_point(Point2D(4, 1)).get_symmetry_index_sets()
        ([0], [])
        >>> MirrorValleyExtended.from_map('''
        ...     .#.##.#.##..###
        ...     ...##...#######
        ...     #.####.#.#.###.
        ...     #..##..##..#...
        ...     ###..###....###
        ...     .##..##..#.#...
        ...     .#....#..######
        ...     #..##..########
        ...     ########.#..#..
        ... ''').fix_point(Point2D(14, 2)).get_symmetry_index_sets()
        ([], [3, 13])
        """
        row_ids, column_ids = self.get_rows_and_columns_ids()
        row_index_set = self.get_last_mirror_index_set(row_ids)
        column_index_set = self.get_last_mirror_index_set(column_ids)
        return row_index_set, column_index_set

    def get_last_mirror_index_set(self, ids: List[int]) -> List[int]:
        """
        >>> MirrorValleyExtended(set(), 0, 0).get_last_mirror_index_set([0, 1, 2, 2, 1, 5, 6])
        []
        >>> MirrorValleyExtended(set(), 0, 0).get_last_mirror_index_set([0, 1, 2, 3, 4, 4, 3, 2, 1])
        [4]
        >>> MirrorValleyExtended(set(), 0, 0).get_last_mirror_index_set([0, 1, 2, 3, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14])
        [3]
        """
        indexes = []
        for last_index in range(len(ids)):
            first_list = ids[:last_index + 1]
            last_list = ids[last_index + 1:][::-1]
            if len(first_list) > len(last_list):
                first_list = first_list[-len(last_list):]
            elif len(first_list) < len(last_list):
                last_list = last_list[-len(first_list):]
            if first_list == last_list:
                indexes.append(last_index)
        return indexes


Challenge.main()
challenge = Challenge()
