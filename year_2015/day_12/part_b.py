#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        65402
        """
        def should_walk(datum: part_a.Json) -> bool:
            return not isinstance(datum, dict) or "red" not in datum.values()
        return part_a.JsonWalker()\
            .get_numbers_sum_from_json(_input, should_walk)


Challenge.main()
challenge = Challenge()
