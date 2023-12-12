#!/usr/bin/env python3
from itertools import count
from math import gcd
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2024.day_08 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1115
        """
        return CityExtended.from_text(_input).get_antinode_count()


class CityExtended(part_a.City):
    def get_antennas_antinodes(self, first: Point2D, second: Point2D) -> List[Point2D]:
        """
        >>>
        >>> sorted(CityExtended(boundaries=(Point2D(0, 0), Point2D(9, 9)), antennas={})\\
        ...     .get_antennas_antinodes(Point2D(0, 0), Point2D(3, 1)))
        [Point2D(x=0, y=0), Point2D(x=3, y=1), Point2D(x=6, y=2), Point2D(x=9, y=3)]
        >>> sorted(CityExtended(boundaries=(Point2D(0, 0), Point2D(9, 9)), antennas={})\\
        ...     .get_antennas_antinodes(Point2D(1, 2), Point2D(3, 1)))
        [Point2D(x=1, y=2), Point2D(x=3, y=1), Point2D(x=5, y=0)]
        >>> _city = CityExtended.from_text('''
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
        !##....#....#
        .#.#....#...
        ..#.##....#.
        ..##...#....
        ....#....#..
        .#...##....#
        ...#..#.....
        #....#.#....
        ..#.....#...
        ....#....#..
        .#........#.
        ...#......##
        >>> _city.get_antinode_count()
        34
        """
        difference = second.difference(first)
        coordinates_gcd = gcd(difference.x, difference.y)
        if coordinates_gcd != 1:
            difference = difference.resize(1 / coordinates_gcd)
        antinodes = []
        for factor in count(0):
            offset_point = first.offset(difference, factor=factor)
            if not self.is_within_bounds(offset_point):
                break
            antinodes.append(offset_point)
        for factor in count(1):
            offset_point = first.offset(difference, factor=-factor)
            if not self.is_within_bounds(offset_point):
                break
            antinodes.append(offset_point)
        return antinodes


Challenge.main()
challenge = Challenge()
