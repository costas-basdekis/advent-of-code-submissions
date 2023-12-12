#!/usr/bin/env python3
from dataclasses import dataclass
from itertools import groupby, combinations
from typing import Dict, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        311
        """
        return City.from_text(_input).get_antinode_count()


@dataclass
class City:
    boundaries: Tuple[Point2D, Point2D]
    antennas: Dict[Point2D, str]

    @classmethod
    def from_text(cls, text: str) -> "City":
        """
        >>> print("!" + str(City.from_text('''
        ...     ............
        ...     ........0...
        ...     .....0......
        ...     .......0....
        ...     ....0.......
        ...     ......A.....
        ...     ............
        ...     ............
        ...     ........A...
        ...     .........A..
        ...     ............
        ...     ............
        ... ''')))
        !............
        ........0...
        .....0......
        .......0....
        ....0.......
        ......A.....
        ............
        ............
        ........A...
        .........A..
        ............
        ............
        """
        lines = text.strip().splitlines()
        boundaries = (
            Point2D(0, 0),
            Point2D(len(lines[0].strip()) - 1 if lines else -1, len(lines) - 1),
        )
        return cls(
            boundaries=boundaries,
            antennas={
                Point2D(x, y): char
                for y, line in enumerate(lines)
                for x, char in enumerate(line.strip())
                if char != "."
            },
        )

    def __str__(self) -> str:
        return self.show()

    def show(self, antinodes: Optional[Set[Point2D]] = None) -> str:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return "\n".join(
            "".join(
                "#"
                if antinodes and point in antinodes else
                char
                if char is not None else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
                for char in [self.antennas.get(point)]
            )
            for y in range(min_y, max_y + 1)
        )

    def get_antinode_count(self) -> int:
        return len(self.get_all_antinodes())

    def get_all_antinodes(self) -> Set[Point2D]:
        """
        >>> _city = City.from_text('''
        ...     ............
        ...     ........0...
        ...     .....0......
        ...     .......0....
        ...     ....0.......
        ...     ......A.....
        ...     ............
        ...     ............
        ...     ........A...
        ...     .........A..
        ...     ............
        ...     ............
        ... ''')
        >>> print("!" + _city.show(antinodes=_city.get_all_antinodes()))
        !......#....#
        ...#....0...
        ....#0....#.
        ..#....0....
        ....0....#..
        .#....#.....
        ...#........
        #......#....
        ........A...
        .........A..
        ..........#.
        ..........#.
        """
        return {
            antinode
            for antennas in self.get_antennas_by_type().values()
            for first, second in combinations(antennas, 2)
            for antinode in self.get_antennas_antinodes(first, second)
            if self.is_within_bounds(antinode)
        }

    def get_antennas_by_type(self) -> Dict[str, List[Point2D]]:
        """
        >>> {_type: len(items) for _type, items in City.from_text('''
        ...     ............
        ...     ........0...
        ...     .....0......
        ...     .......0....
        ...     ....0.......
        ...     ......A.....
        ...     ............
        ...     ............
        ...     ........A...
        ...     .........A..
        ...     ............
        ...     ............
        ... ''').get_antennas_by_type().items()}
        {'0': 4, 'A': 3}
        """
        by_type = lambda point: self.antennas[point]
        return {
            _type: list(items)
            for _type, items in groupby(sorted(self.antennas, key=by_type), key=by_type)
        }

    def get_antennas_antinodes(self, first: Point2D, second: Point2D) -> Tuple[Point2D, Point2D]:
        """
        >>> City.from_text("").get_antennas_antinodes(Point2D(4, 3), Point2D(5, 5))
        (Point2D(x=3, y=1), Point2D(x=6, y=7))
        """
        difference = second.difference(first)
        return first.offset(difference, factor=-1), second.offset(difference)

    def is_within_bounds(self, point: Point2D) -> bool:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return (
            min_x <= point.x <= max_x
            and min_y <= point.y <= max_y
        )


Challenge.main()
challenge = Challenge()
