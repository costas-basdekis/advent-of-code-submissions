#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        170
        """
        return simulate_program(0)


def simulate_program(a: int = 0) -> int:
    b = 0
    if a == 1:
        a = 74107
    else:
        a = 4591
    while a != 1:
        b += 1
        if a % 2 == 0:
            a /= 2
        else:
            a = (a * 3) + 1

    return b


Challenge.main()
challenge = Challenge()
