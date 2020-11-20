#!/usr/bin/env python3
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger):
        """
        >>> Challenge().default_solve()
        42
        """
        return part_a.Minefield.from_rows_text(_input)\
            .add_rows(399999, debugger=debugger)\
            .get_safe_tile_count()


Challenge.main()
challenge = Challenge()
