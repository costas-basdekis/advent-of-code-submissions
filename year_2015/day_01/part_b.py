#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1795
        """
        return get_first_position_under_ground(_input)


def get_first_position_under_ground(text: str) -> int:
    """
    >>> get_first_position_under_ground(")")
    1
    >>> get_first_position_under_ground("()())")
    5
    """
    floor = 0
    for position, content in enumerate(text.strip(), 1):
        if content == "(":
            floor += 1
        elif content == ")":
            floor -= 1
        else:
            raise Exception(f"Unexpected content {repr(content)}")

        if floor == -1:
            return position

    raise Exception(f"Did not go under ground")


Challenge.main()
challenge = Challenge()
