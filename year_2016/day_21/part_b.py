#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        'gdfcabeh'
        """
        return part_a.OperationSet.from_operations_text(_input)\
            .unapply('fbgdceah')


Challenge.main()
challenge = Challenge()
