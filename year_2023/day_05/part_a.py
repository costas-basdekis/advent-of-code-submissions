#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import List, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        806029445
        """
        return Almanac.from_almanac_text(_input).get_lower_seed_location()


@dataclass
class Almanac:
    planted_seeds: List[int]
    seed_to_soil_map: "AlmanacMap"
    soil_to_fertilizer_map: "AlmanacMap"
    fertilizer_to_water_map: "AlmanacMap"
    water_to_light_map: "AlmanacMap"
    light_to_temperature_map: "AlmanacMap"
    temperature_to_humidity_map: "AlmanacMap"
    humidity_to_location_map: "AlmanacMap"

    re_seeds = re.compile(r"seeds:\s*([\d\s]*)")

    @classmethod
    def from_almanac_text(cls, almanac_text: str) -> "Almanac":
        """
        >>> Almanac.from_almanac_text('''
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
        Almanac(planted_seeds=[79, 14, 55, 13],
            seed_to_soil_map=AlmanacMap(map_items=[AlmanacMapItem(source_range=range(98, 100),
            target_start=50), AlmanacMapItem(source_range=range(50, 98),
            target_start=52)]), ...)
        """
        seeds_str, *map_with_header_texts = almanac_text.strip().split("\n\n")

        planted_seeds = \
            list(map(int, cls.re_seeds.match(seeds_str).group(1).split(" ")))
        map_texts_by_header = {
            header: rest
            for map_with_header_text in map_with_header_texts
            for header, rest in [map_with_header_text.strip().split("\n", 1)]
        }

        return cls(
            planted_seeds,
            AlmanacMap.from_map_text(
                map_texts_by_header["seed-to-soil map:"]),
            AlmanacMap.from_map_text(
                map_texts_by_header["soil-to-fertilizer map:"]),
            AlmanacMap.from_map_text(
                map_texts_by_header["fertilizer-to-water map:"]),
            AlmanacMap.from_map_text(
                map_texts_by_header["water-to-light map:"]),
            AlmanacMap.from_map_text(
                map_texts_by_header["light-to-temperature map:"]),
            AlmanacMap.from_map_text(
                map_texts_by_header["temperature-to-humidity map:"]),
            AlmanacMap.from_map_text(
                map_texts_by_header["humidity-to-location map:"]),
        )

    def get_lower_seed_location(self) -> int:
        """
        >>> Almanac.from_almanac_text('''
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
        ... ''').get_lower_seed_location()
        35
        """
        return min(self[seed] for seed in self.planted_seeds)

    def __getitem__(self, item: int) -> int:
        return self.get_map_journey(item)[-1]

    def get_map_journey(self, seed: int) -> List[int]:
        """
        >>> almanac = Almanac.from_almanac_text('''
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
        >>> almanac.get_map_journey(79)
        [79, 81, 81, 81, 74, 78, 78, 82]
        >>> almanac.get_map_journey(14)
        [14, 14, 53, 49, 42, 42, 43, 43]
        >>> almanac.get_map_journey(55)
        [55, 57, 57, 53, 46, 82, 82, 86]
        >>> almanac.get_map_journey(13)
        [13, 13, 52, 41, 34, 34, 35, 35]
        """
        maps = [
            self.seed_to_soil_map,
            self.soil_to_fertilizer_map,
            self.fertilizer_to_water_map,
            self.water_to_light_map,
            self.light_to_temperature_map,
            self.temperature_to_humidity_map,
            self.humidity_to_location_map,
        ]
        journey = [seed]
        result = seed
        for _map in maps:
            result = _map[result]
            journey.append(result)
        return journey

    def translate_range(self, _range: range) -> List[range]:
        return self.get_range_journey(_range)[-1]

    def get_range_journey(self, _range: range) -> List[List[range]]:
        maps = [
            self.seed_to_soil_map,
            self.soil_to_fertilizer_map,
            self.fertilizer_to_water_map,
            self.water_to_light_map,
            self.light_to_temperature_map,
            self.temperature_to_humidity_map,
            self.humidity_to_location_map,
        ]
        journey = [[_range]]
        result = [_range]
        for _map in maps:
            result = _map.translate_ranges(result)
            journey.append(result)
        return journey


@dataclass
class AlmanacMap:
    map_items: List["AlmanacMapItem"]

    @classmethod
    def from_map_text(cls, map_text: str) -> "AlmanacMap":
        """
        >>> AlmanacMap.from_map_text('''
        ...     50 98 2
        ...     52 50 48
        ... ''')
        AlmanacMap(map_items=[AlmanacMapItem(source_range=range(98, 100),
            target_start=50), AlmanacMapItem(source_range=range(50, 98),
            target_start=52)])
        """
        return cls(
            list(map(
                AlmanacMapItem.from_item_text,
                map_text.strip().splitlines(),
            )),
        )

    def __contains__(self, item: int) -> bool:
        return any(item in map_item for map_item in self.map_items)

    def __getitem__(self, item: int) -> int:
        """
        >>> AlmanacMap.from_map_text('''50 98 2\\n52 50 48''')[50]
        52
        >>> AlmanacMap.from_map_text('''50 98 2\\n52 50 48''')[97]
        99
        >>> AlmanacMap.from_map_text('''50 98 2\\n52 50 48''')[98]
        50
        >>> AlmanacMap.from_map_text('''50 98 2\\n52 50 48''')[99]
        51
        >>> AlmanacMap.from_map_text('''50 98 2\\n52 50 48''')[49]
        49
        >>> AlmanacMap.from_map_text('''50 98 2\\n52 50 48''')[100]
        100
        """
        for map_item in self.map_items:
            if item in map_item:
                return map_item[item]

        return item

    def translate_ranges(self, input_ranges: List[range]) -> List[range]:
        translated_ranges = []
        remaining_ranges = input_ranges
        for map_item in self.map_items:
            item_translated_ranges, item_remaining_ranges = \
                map_item.translate_ranges(remaining_ranges)
            translated_ranges.extend(item_translated_ranges)
            remaining_ranges = item_remaining_ranges

        return translated_ranges + remaining_ranges


@dataclass
class AlmanacMapItem:
    source_range: range
    target_start: int

    @classmethod
    def from_item_text(cls, item_text: str) -> "AlmanacMapItem":
        """
        >>> AlmanacMapItem.from_item_text("50 98 2")
        AlmanacMapItem(source_range=range(98, 100), target_start=50)
        """
        target_start, source_start, length = \
            map(int, item_text.strip().split(" "))
        return cls(
            range(source_start, source_start + length), target_start,
        )

    def __contains__(self, item: int) -> bool:
        return item in self.source_range

    def __getitem__(self, item: int) -> int:
        """
        >>> AlmanacMapItem.from_item_text("50 98 2")[98]
        50
        >>> AlmanacMapItem.from_item_text("50 98 2")[99]
        51
        >>> AlmanacMapItem.from_item_text("50 98 2")[97]
        97
        >>> AlmanacMapItem.from_item_text("50 98 2")[100]
        100
        """
        if item not in self:
            return item
        return item - self.source_range.start + self.target_start

    def translate_ranges(
        self, input_ranges: List[range],
    ) -> Tuple[List[range], List[range]]:
        translated_ranges, remaining_ranges = [], []
        for _range in input_ranges:
            item_translated_ranges, item_remaining_ranges = \
                self.translate_range(_range)
            translated_ranges.extend(item_translated_ranges)
            remaining_ranges.extend(item_remaining_ranges)
        return translated_ranges, remaining_ranges

    def translate_range(
        self, input_range: range,
    ) -> Tuple[List[range], List[range]]:
        """
        >>> AlmanacMapItem(range(98, 100), 50).translate_range(range(98, 100))
        ([range(50, 52)], [])
        >>> AlmanacMapItem(range(98, 100), 50).translate_range(range(0, 5))
        ([], [range(0, 5)])
        >>> AlmanacMapItem(range(98, 100), 50).translate_range(range(200, 5))
        ([], [range(200, 5)])
        >>> AlmanacMapItem(range(98, 100), 50).translate_range(range(90, 110))
        ([range(50, 52)], [range(90, 98), range(100, 110)])
        >>> AlmanacMapItem(range(98, 100), 50).translate_range(range(90, 99))
        ([range(50, 51)], [range(90, 98)])
        >>> AlmanacMapItem(range(98, 100), 50).translate_range(range(99, 110))
        ([range(51, 52)], [range(100, 110)])
        """
        input_start = input_range.start
        input_end = input_range.stop - 1
        source_start = self.source_range.start
        source_end = self.source_range.stop - 1

        if input_end < source_start or input_start > source_end:
            return [], [input_range]

        if input_start >= source_start and input_end <= source_end:
            return [
                range(self[input_range.start], self[input_range.stop - 1] + 1),
            ], []

        if input_start < source_start and input_end > source_end:
            return [
                range(self[source_start], self[source_end] + 1),
            ], [
                range(input_start, source_start),
                range(source_end + 1, input_end + 1),
            ]
        elif input_start < source_start:
            return [
                range(self[source_start], self[input_end] + 1),
            ], [
                range(input_start, source_start),
            ]
        else:
            return [
                range(self[input_start], self[source_end] + 1),
            ], [
                range(source_end + 1, input_end + 1),
            ]


Challenge.main()
challenge = Challenge()
