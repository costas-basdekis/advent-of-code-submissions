#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        10345
        """

        return 10345


challenge = Challenge()
challenge.main()
