#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        74
        """
        return get_final_floor(_input)


def get_final_floor(text: str) -> int:
    """
    >>> get_final_floor("(())")
    0
    >>> get_final_floor("()()")
    0
    >>> get_final_floor("(((")
    3
    >>> get_final_floor("(()(()(")
    3
    >>> get_final_floor("))(((((")
    3
    >>> get_final_floor("())")
    -1
    >>> get_final_floor("))(")
    -1
    >>> get_final_floor(")))")
    -3
    >>> get_final_floor(")())())")
    -3
    """
    return text.count("(") - text.count(")")


Challenge.main()
challenge = Challenge()
