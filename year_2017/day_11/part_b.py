#!/usr/bin/env python3
import utils
from year_2017.day_11 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1524
        """
        directions = part_a.DirectionsRotator()\
            .rotate_directions(_input.strip().split(','))
        max_distance = 0
        zero_point = utils.PointHex(0, 0)
        point = zero_point
        for direction in directions:
            point = point.move(direction)
            max_distance = max(max_distance, point.step_distance(zero_point))
        return max_distance


Challenge.main()
challenge = Challenge()
