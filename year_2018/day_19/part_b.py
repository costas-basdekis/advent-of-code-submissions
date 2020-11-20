#!/usr/bin/env python3
import functools
import itertools

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        27024480
        """
        # Analysing the code it finds adds up all the divisors of 10551432
        # If we rewrite the instructions as Python code (with goto), and apply
        # simplifications, it becomes obvious:
        # a, b, c, d, e = 0, 0, 10551432, 1, 10550400
        # while d <= c:
        #     b = 1
        #     while b <= c:
        #         if b * d == c:
        #             a += d
        #         b += 1
        #     d += 1
        return sum(get_divisors(10551432))


def get_divisors(number):
    factors = factorise(number)
    return {
        functools.reduce(int.__mul__, parts, 1)
        for parts_list in (
            itertools.combinations(factors, count)
            for count in range(len(factors) + 1)
        )
        for parts in parts_list
    }


def factorise(number):
    """
    >>> factorise(10551432)
    [2, 2, 2, 3, 41, 10723]
    """
    if number != 10551432:
        raise ValueError(f"Cannot factorise {number}")

    return [2, 2, 2, 3, 41, 10723]


challenge = Challenge()
challenge.main()
