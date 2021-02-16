#!/usr/bin/env python3
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger):
        """
        >>> Challenge().default_solve()
        '10101011110100011'
        """
        return part_a.DataGenerator()\
            .get_disk_checksum(35651584, _input.strip(), debugger=debugger)


Challenge.main()
challenge = Challenge()
