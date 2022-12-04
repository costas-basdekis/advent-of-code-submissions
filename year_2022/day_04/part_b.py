#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_04 import part_a
from year_2022.day_04.part_a import AssignmentPairSet


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        792
        """
        return AssignmentPairSet\
            .from_assignment_pairs_text(_input)\
            .get_overlapping_pair_count()


Challenge.main()
challenge = Challenge()
