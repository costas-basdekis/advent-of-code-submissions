#!/usr/bin/env python3
import utils
from year_2018.day_20 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        8520
        """
        distances = part_a.Area.from_instruction_text(_input)\
            .get_room_distances()
        return sum(
            1
            for distance in distances.values()
            if distance >= 1000
        )


Challenge.main()
challenge = Challenge()
