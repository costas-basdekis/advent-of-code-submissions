#!/usr/bin/env python3
import utils
from year_2018.day_21 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        313035
        """
        return get_last_acceptable_a()


def get_last_acceptable_a(start=0):
    value = start
    previous_value = None
    seen = set()
    while value not in seen:
        seen.add(value)
        previous_value = value
        value = part_a.get_acceptable_a(value)

    return previous_value


Challenge.main()
challenge = Challenge()
