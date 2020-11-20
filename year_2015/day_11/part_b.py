#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        'cqkaabcc'
        """
        return part_a.Password(_input.strip())\
            .get_next_password(debugger=debugger)\
            .get_next_password(debugger=debugger)


Challenge.main()
challenge = Challenge()
