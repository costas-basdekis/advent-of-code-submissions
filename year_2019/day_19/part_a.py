#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_05.part_b import get_program_result_and_output_extended
import year_2019.day_09.part_a


def solve(_input=None):
    """
    >>> solve()
    189
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    scan = scan_area(_input, 50, 50)

    return sum(point for line in scan for point in line)


def scan_area(program_text, width, height):
    return [
        [
            get_program_result_and_output_extended(program_text, [x, y])[1][0]
            for x in range(width)
        ]
        for y in range(height)
    ]


def show_scan(scan):
    return "\n".join(
        "".join(
            str(point)
            for point in line
        )
        for line in scan
    )


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print(f"Solution:\n{solve()}")
