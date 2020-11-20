#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2018.day_04.part_a import Observations


def solve(_input=None):
    """
    >>> solve()
    49944
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    sleepiest_profile = Observations.from_lines(_input).attach_guard_ids()\
        .get_sleep_schedule()\
        .get_guards_sleep_profiles()\
        .get_sleepiest_profile_by_strategy_2()
    if not sleepiest_profile:
        raise Exception("No sleepiest profile")

    return sleepiest_profile.get_signature()


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
