#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_21.part_a import SpringScript, run_spring_robot


def solve(_input=None):
    """
    >>> solve()
    1139206699
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return run_spring_robot(get_extended_script(), _input, running=True)


def get_extended_script():
    """
    >>> script = get_extended_script()
    >>> script.simulate("#####.###########", True)
    >>> script.simulate("#####.##.##..####", True)
    >>> script.simulate("#####.#.#...#####", True)
    """

    return SpringScript()\
        .not_('A', 'J')\
        .not_('C', 'T')\
        .or_('T', 'J')\
        .not_('B', 'T')\
        .or_('T', 'J')\
        .and_('D', 'J')\
        .set_('E', 'T')\
        .or_('H', 'T')\
        .and_('T', 'J')


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
