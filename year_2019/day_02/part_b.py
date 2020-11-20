#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_02.part_a import get_program_result


def solve(_input=None):
    """
    >>> solve()
    8226
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    noun, verb = find_verb_and_noun(_input, 19690720)

    return 100 * noun + verb


def find_verb_and_noun(program_text, expected_value):
    """
    >>> _input = get_current_directory(__file__)\
        .joinpath("part_a_input.txt")\
        .read_text()
    >>> find_verb_and_noun(_input, 2890696)
    (12, 2)
    >>> find_verb_and_noun(_input, 19690720)
    (82, 26)
    """
    for noun in range(100):
        for verb in range(100):
            value = get_program_result(program_text, {1: noun, 2: verb})
            if value == expected_value:
                return noun, verb

    raise Exception(f"Could not find and noun to result in {expected_value}")


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
