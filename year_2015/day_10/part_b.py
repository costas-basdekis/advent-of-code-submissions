#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        3579328
        """
        return part_a.LookAndSay().get_length_after_steps(
            _input.strip(), 50, debugger=debugger)


Challenge.main()
challenge = Challenge()
