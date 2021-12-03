#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_06 import part_a
from year_2021.day_06.part_a import School


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1605400130036
        """
        return School.from_school_text(_input).advance_many(256).fish_count


Challenge.main()
challenge = Challenge()
