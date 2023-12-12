#!/usr/bin/env python3
from functools import cached_property
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge, Direction
from year_2024.day_12 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        899196
        """
        return GardenExtended.from_text(_input).get_total_regions_price()


class GardenExtended(part_a.Garden):
    @cached_property
    def perimeter(self) -> int:
        """
        >>> _garden = GardenExtended.from_text('''
        ...     AAAA
        ...     BBCD
        ...     BBCC
        ...     EEEC
        ... ''')
        >>> _regions = _garden.get_regions()
        >>> sorted(((min(_region.plants.values()), _region.perimeter) for _region in _regions), key=lambda item: min(item[0]))
        [('A', 4, 4, 16), ('B', 4, 4, 16), ('C', 4, 8, 32), ('D', 1, 4, 4), ('E', 3, 4, 12)]
        >>> GardenExtended.from_text('''
        ...     AAAA
        ...     BBCD
        ...     BBCC
        ...     EEEC
        ... ''').get_total_regions_price()
        80
        >>> GardenExtended.from_text('''
        ...     OOOOO
        ...     OXOXO
        ...     OOOOO
        ...     OXOXO
        ...     OOOOO
        ... ''').get_total_regions_price()
        436
        >>> GardenExtended.from_text('''
        ...     RRRRIICCFF
        ...     RRRRIICCCF
        ...     VVRRRCCFFF
        ...     VVRCCCJFFF
        ...     VVVVCJJCFE
        ...     VVIVCCJJEE
        ...     VVIIICJJEE
        ...     MIIIIIJJEE
        ...     MIIISIJEEE
        ...     MMMISSJEEE
        ... ''').get_total_regions_price()
        1206
        >>> GardenExtended.from_text('''
        ...     EEEEE
        ...     EXXXX
        ...     EEEEE
        ...     EXXXX
        ...     EEEEE
        ... ''').get_total_regions_price()
        236
        >>> GardenExtended.from_text('''
        ...     AAAAAA
        ...     AAABBA
        ...     AAABBA
        ...     ABBAAA
        ...     ABBAAA
        ...     AAAAAA
        ... ''').get_total_regions_price()
        367
        """
        return sum(
            1
            for point in self.plants
            for direction in Direction
            for neighbour in [point.offset(direction.offset)]
            if neighbour not in self.plants
            for previous_point in [point.offset(direction.clockwise.offset)]
            for previous_neighbour in [previous_point.offset(direction.offset)]
            if not (
                previous_point in self.plants
                and previous_neighbour not in self.plants
            )
        )


Challenge.main()
challenge = Challenge()
