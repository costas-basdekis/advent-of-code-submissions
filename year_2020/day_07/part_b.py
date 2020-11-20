#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2020.day_07 import part_a


def solve(_input=None):
    """
    >>> solve()
    82930
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _, content_count = part_a.BagRuleSet.from_bag_rule_set_text(_input)\
        .get_eventual_contents()

    return content_count["shiny gold"] - 1


if __name__ == '__main__':
    if doctest.testmod(part_a).failed or doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
