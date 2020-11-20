#!/usr/bin/env python3
import doctest
import itertools

from utils import get_current_directory
from year_2019.day_04.part_a import is_password_valid, count_valid_passwords


def solve(_input=None):
    """
    >>> solve()
    1390
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
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


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
