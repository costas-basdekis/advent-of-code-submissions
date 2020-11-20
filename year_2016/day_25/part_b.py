#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        42
        """
        return 42


Challenge.main()
challenge = Challenge()
