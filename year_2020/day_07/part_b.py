#!/usr/bin/env python3
import utils

from year_2020.day_07 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        82930
        """
        _, content_count = part_a.BagRuleSet.from_bag_rule_set_text(_input)\
            .get_eventual_contents()

        return content_count["shiny gold"] - 1


Challenge.main()
challenge = Challenge()
