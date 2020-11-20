#!/usr/bin/env python3
import doctest
import re

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    416
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    password_entries = parse_password_db(_input)
    return get_valid_password_count(password_entries)


def is_password_entry_valid(entry):
    """
    >>> is_password_entry_valid(('a', 1, 3, 'abcde'))
    True
    >>> is_password_entry_valid(('b', 1, 3, 'cdefg'))
    False
    >>> is_password_entry_valid(('c', 2, 9, 'ccccccccc'))
    True
    """
    character, min_count, max_count, password = entry
    return min_count <= password.count(character) <= max_count


def get_valid_password_count(entries, valid_func=is_password_entry_valid):
    return sum(
        1
        for entry in entries
        if valid_func(entry)
    )


re_password_entry = re.compile(r"^(\d+)-(\d+) (\w): (.*)$")


def parse_password_db(password_db_text):
    """
    >>> parse_password_db(
    ...     "1-3 a: abcde\\n"
    ...     "1-3 b: cdefg\\n"
    ...     "2-9 c: ccccccccc\\n"
    ... )
    [('a', 1, 3, 'abcde'), ('b', 1, 3, 'cdefg'), ('c', 2, 9, 'ccccccccc')]
    """
    lines = password_db_text.splitlines()
    non_empty_lines = filter(None, lines)
    return [
        (character, int(min_count_str), int(max_count_str), password)
        for min_count_str, max_count_str, character, password in (
            re_password_entry.match(line).groups()
            for line in non_empty_lines
        )
    ]


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
