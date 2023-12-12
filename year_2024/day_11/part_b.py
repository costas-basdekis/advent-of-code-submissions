#!/usr/bin/env python3
from typing import Dict, List, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_11 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        237149922829154
        """
        return StonehengeExtended.from_text(_input).get_count_after_blinks(75)


class StonehengeExtended(part_a.Stonehenge):
    def get_count_after_blinks(self, count: int) -> int:
        """
        >>> StonehengeExtended.from_text("125 17").get_count_after_blinks(25)
        55312
        """
        cache = {}
        return sum(
            self.get_count_for_stone_after_blinks_with_cache(stone, count, cache)
            for stone in self.stones
        )

    def get_count_for_stone_after_blinks_with_cache(self, stone: int, count: int, cache: Dict[int, Dict[int, int]]) -> int:
        if count == 0:
            return 1
        stone_count = cache.setdefault(stone, {}).get(count)
        if stone_count is None:
            new_stones = StonehengeExtended([stone]).blink_once().stones
            stone_count = cache[stone][count] = sum(
                self.get_count_for_stone_after_blinks_with_cache(new_stone, count - 1, cache)
                for new_stone in new_stones
            )
        return stone_count

    def blink_many(self: "StonehengeExtended", count: int) -> "StonehengeExtended":
        """
        >>> print(StonehengeExtended.from_text("125 17").blink_many(6))
        2097446912 14168 4048 2 0 2 4 40 48 2024 40 48 80 96 2 8 6 7 6 0 3 2
        """
        henge = self
        cache: Dict[int, List[int]] = {}
        for _ in range(count):
            henge = henge.blink_once_with_cache(cache)
        return henge

    def blink_once_with_cache(self: "StonehengeExtended", cache: Dict[int, List[int]]) -> "StonehengeExtended":
        """
        >>> _cache = {}
        >>> print(StonehengeExtended.from_text("0 1 10 99 999").blink_once_with_cache(_cache))
        1 2024 1 0 9 9 2021976
        >>> print(StonehengeExtended.from_text("0 1 10 99 999").blink_once_with_cache(_cache))
        1 2024 1 0 9 9 2021976
        """
        cls = type(self)
        # noinspection PyArgumentList
        return cls(stones=[
            new_stone
            for stone in self.stones
            for new_stone in self.blink_stone_with_cache(stone, cache=cache)
        ])

    def blink_stone_with_cache(self, stone: int, cache: Dict[int, List[int]]) -> List[int]:
        """
        >>> _cache = {}
        >>> [StonehengeExtended([]).blink_stone_with_cache(_stone, _cache) for _stone in [0, 1, 2, 10, 100, 1234]]
        [[1], [2024], [4048], [1, 0], [202400], [12, 34]]
        >>> [StonehengeExtended([]).blink_stone_with_cache(_stone, _cache) for _stone in [0, 1, 2, 10, 100, 1234]]
        [[1], [2024], [4048], [1, 0], [202400], [12, 34]]
        """
        if stone not in cache:
            cache[stone] = super().blink_stone(stone)
        return cache[stone]


Challenge.main()
challenge = Challenge()
