#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1038736
        """
        return part_a.Hasher(_input.strip())\
            .get_lowest_index_with_zeros(zero_count=6, debugger=debugger)


Challenge.main()
challenge = Challenge()
