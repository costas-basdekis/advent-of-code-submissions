#!/usr/bin/env python3
import utils
from year_2017.day_21 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2758764
        """
        return part_a.Book.from_book_text(_input)\
            .step_grid_many(18, debug=debug)\
            .get_pixel_count()


challenge = Challenge()
challenge.main()
