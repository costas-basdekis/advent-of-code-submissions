#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_24.part_a import find_first_valid_input


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        11721151118175
        """
        return find_minimum_valid_input(debugger=debugger)


def find_minimum_valid_input(
    debugger: Debugger = Debugger(enabled=False),
) -> int:
    return find_first_valid_input(range(1, 9), debugger=debugger)


Challenge.main()
challenge = Challenge()
