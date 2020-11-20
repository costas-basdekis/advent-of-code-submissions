#!/usr/bin/env python3
import itertools
import math

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        917
        """
        return get_prime_count(range(106500, 123500 + 1, 17))


def get_prime_count(numbers):
    return sum(
        1
        for number in numbers
        if not is_prime(number)
    )


def is_prime(number):
    if number <= 1:
        return False
    return all(
        number % divisor
        for divisor
        in itertools.islice(itertools.count(2), int(math.sqrt(number) - 1))
    )


challenge = Challenge()
challenge.main()
