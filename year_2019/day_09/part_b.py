#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_05.part_b import get_program_result_and_output_extended
import year_2019.day_09.part_a


def solve(_input=None):
    """
    >>> solve()
    50894
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _, output_stream = get_program_result_and_output_extended(_input, [2])

    coordinates, = output_stream
    return coordinates


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
