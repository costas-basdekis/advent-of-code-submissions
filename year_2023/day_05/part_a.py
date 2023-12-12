#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, Cls, Self,
)


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


Challenge.main()
challenge = Challenge()
