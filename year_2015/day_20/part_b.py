#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge, factorise
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        786240
        """
        return SantaExtended().get_min_house_number_with_at_least_present_count(
            int(_input), debugger=debugger)


class SantaExtended(part_a.Santa):
    def get_house_present_count(self, house_number: int) -> int:
        """
        >>> list(map(SantaExtended().get_house_present_count, range(1, 10)))
        [11, 33, 44, 77, 66, 132, 88, 165, 143]
        """
        all_factors = factorise(house_number)
        eligible_factors = [
            factor
            for factor in all_factors
            if house_number // factor <= 50
        ]
        return sum(eligible_factors) * 11



Challenge.main()
challenge = Challenge()
