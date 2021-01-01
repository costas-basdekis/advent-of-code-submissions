#!/usr/bin/env python3
import itertools

import utils

from year_2019.day_04.part_a import is_password_valid, count_valid_passwords


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        1390
        """
        _range = _input.strip().split("-")
        return count_valid_passwords(_range, is_password_valid_complete)


def is_password_valid_complete(password, _range=None):
    """
    >>> is_password_valid_complete('111')
    False
    >>> is_password_valid_complete('1111111')
    False
    >>> is_password_valid_complete('111123')
    False
    >>> is_password_valid_complete('135679')
    False
    >>> is_password_valid_complete('122345')
    True
    >>> is_password_valid_complete('111111')
    False
    >>> is_password_valid_complete('223450')
    False
    >>> is_password_valid_complete('123789')
    False
    >>> is_password_valid_complete('112233')
    True
    >>> is_password_valid_complete('123444')
    False
    >>> is_password_valid_complete('111122')
    True
    >>> is_password_valid_complete('555558')
    False
    >>> is_password_valid_complete('555588')
    True
    >>> is_password_valid_complete('111111', ('128392', '643281'))
    False
    >>> is_password_valid_complete('111111', ('000000', '643281'))
    False
    >>> is_password_valid_complete('111111', ('111111', '643281'))
    False
    """
    if not is_password_valid(password, _range):
        return False
    digits_groups = [
        tuple(digits)
        for _, digits in itertools.groupby(password)
    ]
    digits_lengths = set(map(len, digits_groups))
    if 2 not in digits_lengths:
        return False

    return True


challenge = Challenge()
challenge.main()
