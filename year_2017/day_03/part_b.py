#!/usr/bin/env python3
import itertools

import utils
from year_2017.day_03 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        349975
        """
        return max(GridExtended().stress_test(int(_input)).values())


class GridExtended(part_a.Grid):
    def stress_test(self, min_value):
        values = {self.get_point_for_index(1): 1}
        for index in itertools.count(2):
            point = self.get_point_for_index(index)
            value = sum(
                values[neighbour]
                for neighbour in point.get_euclidean_neighbours()
                if neighbour in values
            )
            values[point] = value
            if value >= min_value:
                break

        return values


challenge = Challenge()
challenge.main()
