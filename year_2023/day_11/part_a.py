#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        9312968
        """
        return Universe.from_universe_map(_input)\
            .expand_empty_rows_and_columns()\
            .get_sum_of_shortest_paths()


@dataclass
class Universe:
    galaxies: List[Point2D]

    @classmethod
    def from_universe_map(cls, universe_map: str) -> "Universe":
        """
        >>> _universe = Universe.from_universe_map('''
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
        >>> print("!" + str(_universe))
        !...#......
        .......#..
        #.........
        ..........
        ......#...
        .#........
        .........#
        ..........
        .......#..
        #...#.....
        """
        galaxies = [
            Point2D(x, y)
            for y, line in enumerate(universe_map.strip().splitlines())
            for x, char in enumerate(line.strip())
            if char == "#"
        ]
        return cls(galaxies=galaxies)

    def __str__(self) -> str:
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.galaxies)
        return "\n".join(
            "".join(
                "#"
                if Point2D(x, y) in self.galaxies else
                "."
                for x in range(min_x, max_x + 1)
            )
            for y in range(min_y, max_y + 1)
        )

    def get_sum_of_shortest_paths(self) -> int:
        """
        >>> _universe = Universe.from_universe_map('''
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
        ... ''').expand_empty_rows_and_columns()
        >>> _universe.get_sum_of_shortest_paths()
        374
        """
        return sum(
            self.galaxies[left_index].manhattan_distance(self.galaxies[right_index])
            for left_index in range(len(self.galaxies))
            for right_index in range(left_index + 1, len(self.galaxies))
        )

    def expand_empty_rows_and_columns(self, expansion_count: int = 1) -> "Universe":
        """
        >>> _universe = Universe.from_universe_map('''
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
        >>> print("!" + str(_universe.expand_empty_rows_and_columns()))
        !....#........
        .........#...
        #............
        .............
        .............
        ........#....
        .#...........
        ............#
        .............
        .............
        .........#...
        #....#.......
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.galaxies)
        empty_columns_indexes = set(range(min_x, max_x + 1))
        empty_rows_indexes = set(range(min_y, max_y + 1))
        for galaxy in self.galaxies:
            if galaxy.x in empty_columns_indexes:
                empty_columns_indexes.remove(galaxy.x)
            if galaxy.y in empty_rows_indexes:
                empty_rows_indexes.remove(galaxy.y)
        columns_added_before = {}
        rows_added_before = {}
        columns_added_before_count = 0
        for x in range(min_x, max_x + 1):
            columns_added_before[x] = columns_added_before_count
            if x in empty_columns_indexes:
                columns_added_before_count += expansion_count
        rows_added_before_count = 0
        for x in range(min_x, max_x + 1):
            rows_added_before[x] = rows_added_before_count
            if x in empty_rows_indexes:
                rows_added_before_count += expansion_count
        galaxies = [
            Point2D(
                galaxy.x + columns_added_before[galaxy.x],
                galaxy.y + rows_added_before[galaxy.y],
            )
            for galaxy in self.galaxies
        ]
        cls = type(self)
        return cls(galaxies=galaxies)


Challenge.main()
challenge = Challenge()
