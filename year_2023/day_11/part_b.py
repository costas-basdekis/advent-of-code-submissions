#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_11 import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> _universe = part_a.Universe.from_universe_map('''
        ...     ...#......
        ...     .......#..
        ...     #.........
        ...     ..........
        ...     ......#...
        ...     .#........
        ...     .........#
        ...     ..........
        ...     .......#..
        ...     #...#.....
        ... ''')
        >>> _universe.expand_empty_rows_and_columns(10 - 1).get_sum_of_shortest_paths()
        1030
        >>> _universe.expand_empty_rows_and_columns(100 - 1).get_sum_of_shortest_paths()
        8410
        >>> solution = Challenge().default_solve()
        >>> solution < 597714715262
        True
        >>> solution
        597714117556
        """
        return part_a.Universe.from_universe_map(_input)\
            .expand_empty_rows_and_columns(1000000 - 1)\
            .get_sum_of_shortest_paths()


Challenge.main()
challenge = Challenge()
