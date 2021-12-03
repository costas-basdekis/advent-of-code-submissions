#!/usr/bin/env python3
from itertools import starmap
from typing import List

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_01.part_a import Depths


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1781
        """
        return DepthsExtended.from_depths_text(_input)\
            .triple_sum()\
            .get_increasing_differences_count()


class DepthsExtended(Depths):
    def triple_sum(self) -> "DepthsExtended":
        """
        >>> DepthsExtended(depths=[
        ...     199, 200, 208, 210, 200, 207, 240, 269, 260, 263
        ... ]).triple_sum()
        DepthsExtended(depths=[607, 618, 618, 617, 647, 716, 769, 792])
        >>> DepthsExtended(depths=[
        ...     199, 200, 208, 210, 200, 207, 240, 269, 260, 263
        ... ]).triple_sum().get_increasing_differences_count()
        5
        """
        triple_depths = list(map(
            sum,
            zip(self.depths, self.depths[1:], self.depths[2:]),
        ))
        return type(self)(
            depths=triple_depths,
        )


Challenge.main()
challenge = Challenge()
