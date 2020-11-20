#!/usr/bin/env python3
from itertools import count

from aox.challenge import Debugger
from utils import BaseChallenge, factorise


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        776160
        """
        return Santa().get_min_house_number_with_at_least_present_count(
            int(_input), debugger=debugger)


class Santa:
    def get_min_house_number_with_at_least_present_count(
            self, min_present_count: int,
            debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> Santa().get_min_house_number_with_at_least_present_count(100)
        6
        """
        max_present_count_seen = None
        debugger.reset()
        for house_number in debugger.stepping(count(1)):
            present_count = self.get_house_present_count(house_number)
            if present_count >= min_present_count:
                return house_number
            if max_present_count_seen is None \
                    or present_count > max_present_count_seen:
                max_present_count_seen = present_count
            if debugger.should_report():
                debugger.default_report(
                    f"max presents: {max_present_count_seen}"
                    f"/{min_present_count}")

    def get_house_present_count(self, house_number: int) -> int:
        """
        >>> list(map(Santa().get_house_present_count, range(1, 10)))
        [10, 30, 40, 70, 60, 120, 80, 150, 130]
        """
        factors = factorise(house_number)
        return sum(factors) * 10


Challenge.main()
challenge = Challenge()
