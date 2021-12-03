#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from year_2015.day_23 import part_a
from year_2015.day_23.part_a import simulate_program


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        247
        """
        return simulate_program(1)


Challenge.main()
challenge = Challenge()
