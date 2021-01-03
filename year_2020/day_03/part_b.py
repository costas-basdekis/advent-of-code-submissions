#!/usr/bin/env python3
import utils

from year_2020.day_03.part_a import TreeMap


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        4723283400
        """
        return TreeMap.from_text(_input)\
            .get_product_of_tree_counts_on_slopes(
                [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)])


challenge = Challenge()
challenge.main()
