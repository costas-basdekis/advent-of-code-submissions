#!/usr/bin/env python3
import utils

from year_2018.day_05 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        5898
        """
        _, length = part_a.Polymer(_input.strip()).find_worst_blockage()

        return length


Challenge.main()
challenge = Challenge()
