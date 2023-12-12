#!/usr/bin/env python3
from typing import List, Optional, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_17 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return PoolExtended.from_map(_input).find_minimum_heat_loss(debugger=debugger)


class PoolExtended(part_a.Pool):
    @classmethod
    def from_map(cls, text: str, valid_lengths: Optional[List[int]] = None) -> "PoolExtended":
        """
        >>> PoolExtended.from_map('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... ''').find_minimum_heat_loss()
        94
        >>> PoolExtended.from_map('''
        ...     111111111111
        ...     999999999991
        ...     999999999991
        ...     999999999991
        ...     999999999991
        ... ''').find_minimum_heat_loss()
        71
        """
        if valid_lengths is None:
            valid_lengths = [4, 5, 6, 7, 8, 9, 10]
        return super().from_map(text, valid_lengths)


Challenge.main()
challenge = Challenge()
