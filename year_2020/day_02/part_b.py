#!/usr/bin/env python3
import utils

from year_2020.day_02.part_a import parse_password_db, get_valid_password_count


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        688
        """
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


Challenge.main()
challenge = Challenge()
