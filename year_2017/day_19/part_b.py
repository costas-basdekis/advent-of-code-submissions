#!/usr/bin/env python3
import utils
from year_2017.day_19 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        16408
        """
        return part_a.Diagram.from_diagram_text(_input).get_step_count()


challenge = Challenge()
challenge.main()
