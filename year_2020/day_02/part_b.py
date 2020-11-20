#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2020.day_02.part_a import parse_password_db, get_valid_password_count


def solve(_input=None):
    """
    >>> solve()
    688
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    password_entries = parse_password_db(_input)
    return get_valid_password_count(
        password_entries, is_password_entry_valid_alternate)


def is_password_entry_valid_alternate(entry):
    """
    >>> is_password_entry_valid_alternate(('a', 1, 3, 'abcde'))
    True
    >>> is_password_entry_valid_alternate(('b', 1, 3, 'cdefg'))
    False
    >>> is_password_entry_valid_alternate(('c', 2, 9, 'ccccccccc'))
    False
    """
    character, first_position, second_position, password = entry
    is_in_first_position = password[first_position - 1] == character
    is_in_second_position = password[second_position - 1] == character

    return is_in_first_position != is_in_second_position


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
