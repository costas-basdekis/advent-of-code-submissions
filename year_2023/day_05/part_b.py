#!/usr/bin/env python3
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_05 import part_a
from year_2023.day_05.part_a import Almanac


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        59370572
        """
        return AlmanacExtended\
            .from_almanac_text(_input)\
            .get_lower_seed_location()


class AlmanacExtended(Almanac):
    def get_lower_seed_location(self) -> int:
        """
        >>> almanac = AlmanacExtended.from_almanac_text('''
        ...     seeds: 79 14 55 13
        ...
        ...     seed-to-soil map:
        ...     50 98 2
        ...     52 50 48
        ...
        ...     soil-to-fertilizer map:
        ...     0 15 37
        ...     37 52 2
        ...     39 0 15
        ...
        ...     fertilizer-to-water map:
        ...     49 53 8
        ...     0 11 42
        ...     42 0 7
        ...     57 7 4
        ...
        ...     water-to-light map:
        ...     88 18 7
        ...     18 25 70
        ...
        ...     light-to-temperature map:
        ...     45 77 23
        ...     81 45 19
        ...     68 64 13
        ...
        ...     temperature-to-humidity map:
        ...     0 69 1
        ...     1 0 69
        ...
        ...     humidity-to-location map:
        ...     60 56 37
        ...     56 93 4
        ... ''')
        >>> almanac.get_lower_seed_location()
        46
        """
        return min(
            translated_range.start
            for seed_range in self.get_seed_ranges()
            for translated_range in self.translate_range(seed_range)
        )

    def get_seed_ranges(self) -> List[range]:
        return [
            range(start, start + length)
            for index in range(0, len(self.planted_seeds), 2)
            for start, length in [self.planted_seeds[index:index + 2]]
        ]


Challenge.main()
challenge = Challenge()
