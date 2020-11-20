#!/usr/bin/env python3
import doctest

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    2050
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _range = _input.strip().split("-")
    return count_valid_passwords(_range)


def count_valid_passwords(_range):
    """
    >>> count_valid_passwords(map(password_from_number, (100000, 50000)))
    0
    >>> count_valid_passwords(map(password_from_number, (111111, 111111)))
    1
    >>> count_valid_passwords(map(password_from_number, (123455, 123456)))
    1
    """
    return sum(
        1
        for number in passwords_in_range(_range)
        if is_password_valid(password_from_number(number))
    )


def passwords_in_range(_range):
    """
    >>> list(passwords_in_range(("0", "5")))
    [0, 1, 2, 3, 4, 5]
    >>> list(passwords_in_range(("10", "5")))
    []
    >>> len(list(passwords_in_range((111111, 111111))))
    1
    >>> len(list(passwords_in_range((123455, 123456))))
    2
    >>> len(list(passwords_in_range(("128392", "643281"))))
    514890
    """
    min_password, max_password = _range
    min_number, max_number = int(min_password), int(max_password)
    return range(min_number, max_number + 1)


def password_from_number(number):
    """
    >>> password_from_number(0)
    '000000'
    >>> password_from_number(1)
    '000001'
    >>> password_from_number(22)
    '000022'
    >>> password_from_number(123456)
    '123456'
    """
    return str(number).rjust(6, "0")


def is_password_valid(password, _range=None):
    """
    >>> is_password_valid('111')
    False
    >>> is_password_valid('1111111')
    False
    >>> is_password_valid('111123')
    True
    >>> is_password_valid('135679')
    False
    >>> is_password_valid('122345')
    True
    >>> is_password_valid('111111')
    True
    >>> is_password_valid('223450')
    False
    >>> is_password_valid('123789')
    False
    >>> is_password_valid('111111', ('128392', '643281'))
    False
    >>> is_password_valid('111111', ('000000', '643281'))
    True
    >>> is_password_valid('111111', ('111111', '643281'))
    True
    """
    if len(password) != 6:
        return False
    pairs = [password[index:index + 2] for index in range(len(password) - 1)]
    if not any(a == b for a, b in pairs):
        return False
    if any(int(a) > int(b) for a, b in pairs):
        return False
    if _range:
        min_password, max_password = _range
        if not (min_password <= password <= max_password):
            return False
        # This should be have exactly as the above.
        # But we're just being paranoid
        if not (int(min_password) <= int(password) <= int(max_password)):
            return False

    return True


if __name__ == '__main__':
    doctest.testmod()
    print("Tests passed")
    print("Solution:", solve())
