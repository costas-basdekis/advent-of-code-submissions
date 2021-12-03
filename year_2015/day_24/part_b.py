#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from year_2015.day_24 import part_a
from year_2015.day_24.part_a import PackageSet


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        80393059
        """
        return PackageSet\
            .of_group_count(4)\
            .from_packages_text(_input)\
            .first_group_quantum_entanglement


Challenge.main()
challenge = Challenge()
