#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2024.day_13 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        76358113886726
        """
        return ArcadeExtended.from_text(_input).fix_machines().get_winning_cost()


class ArcadeExtended(part_a.Arcade):
    def fix_machines(self) -> "ArcadeExtended":
        offset = Point2D(10000000000000, 10000000000000)
        return ArcadeExtended(machines=[
            part_a.Machine(
                a_offset=machine.a_offset,
                b_offset=machine.b_offset,
                target=machine.target.offset(offset),
            )
            for machine in self.machines
        ])


Challenge.main()
challenge = Challenge()
