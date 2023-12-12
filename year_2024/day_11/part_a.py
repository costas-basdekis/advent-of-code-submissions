#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        199982
        """
        return Stonehenge.from_text(_input).get_count_after_blinks(25)


@dataclass
class Stonehenge:
    stones: List[int]

    @classmethod
    def from_text(cls, text: str) -> "Stonehenge":
        """
        >>> print(Stonehenge.from_text("0 1 10 99 999"))
        0 1 10 99 999
        """
        return cls(stones=list(map(int, text.strip().split(" "))))

    def __str__(self) -> str:
        return " ".join(map(str, self.stones))

    def get_count_after_blinks(self, count: int) -> int:
        """
        >>> Stonehenge.from_text("125 17").get_count_after_blinks(25)
        55312
        """
        return len(self.blink_many(count).stones)

    def blink_many(self: Self["Stonehenge"], count: int) -> Self["Stonehenge"]:
        """
        >>> print(Stonehenge.from_text("125 17").blink_many(6))
        2097446912 14168 4048 2 0 2 4 40 48 2024 40 48 80 96 2 8 6 7 6 0 3 2
        """
        henge = self
        for _ in range(count):
            henge = henge.blink_once()
        return henge

    def blink_once(self: Self["Stonehenge"]) -> Self["Stonehenge"]:
        """
        >>> print(Stonehenge.from_text("0 1 10 99 999").blink_once())
        1 2024 1 0 9 9 2021976
        """
        cls = type(self)
        return cls(stones=[
            new_stone
            for stone in self.stones
            for new_stone in self.blink_stone(stone)
        ])

    def blink_stone(self, stone: int) -> List[int]:
        """
        >>> [Stonehenge([]).blink_stone(_stone) for _stone in [0, 1, 2, 10, 100, 1234]]
        [[1], [2024], [4048], [1, 0], [202400], [12, 34]]
        """
        if stone == 0:
            return [1]
        stone_str = str(stone)
        if len(stone_str) % 2 == 0:
            return [int(stone_str[:len(stone_str) // 2]), int(stone_str[len(stone_str) // 2:])]
        return [stone * 2024]


Challenge.main()
challenge = Challenge()
