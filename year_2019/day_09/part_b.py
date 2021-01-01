#!/usr/bin/env python3
import utils

from year_2019.day_05.part_b import get_program_result_and_output_extended
import year_2019.day_09.part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        50894
        """
        _, output_stream = get_program_result_and_output_extended(_input, [2])

        coordinates, = output_stream
        return coordinates


challenge = Challenge()
challenge.main()
