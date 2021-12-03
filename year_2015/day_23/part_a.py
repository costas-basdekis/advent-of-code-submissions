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


def simulate_program(a: int) -> int:
    b = 0
    if a == 1:
        value = get_constant_for_1()
    elif a == 0:
        value = get_constant_for_0()
    else:
        raise Exception(f"Cannot get constant for a='{a}'")
    while value != 1:
        b += 1
        if value % 2 == 0:
            value /= 2
        else:
            value = (value * 3) + 1

    return b


def get_constant_for_0() -> int:
    """
    >>> get_constant_for_0()
    4591
    """
    return get_constant_for_program("""
        inc a
        inc a
        tpl a
        tpl a
        tpl a
        inc a
        inc a
        tpl a
        inc a
        inc a
        tpl a
        tpl a
        tpl a
        inc a
    """, a=0)


def get_constant_for_1() -> int:
    """
    >>> get_constant_for_1()
    113383
    """
    return get_constant_for_program("""
        tpl a
        inc a
        inc a
        tpl a
        inc a
        inc a
        tpl a
        tpl a
        inc a
        inc a
        tpl a
        inc a
        tpl a
        inc a
        tpl a
        inc a
        inc a
        tpl a
        inc a
        tpl a
        tpl a
        inc a
    """, a=1)


def get_constant_for_program(program_text: str, a: int) -> int:
    data = {
        "a": a,
    }

    def increase_a():
        data["a"] += 1

    def triple_a():
        data["a"] *= 3

    instruction_mapping = {
        "inc a": increase_a,
        "tpl a": triple_a,
    }

    lines = filter(None, map(str.strip, program_text.splitlines()))
    for line in lines:
        instruction_mapping[line]()

    return data["a"]


Challenge.main()
challenge = Challenge()
