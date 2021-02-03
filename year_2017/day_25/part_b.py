#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        42
        """
        return 42


Challenge.main()
challenge = Challenge()
