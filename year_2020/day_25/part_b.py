#!/usr/bin/env python3
import utils
from year_2020.day_25 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        42
        """
        return 42


challenge = Challenge()
challenge.main()
