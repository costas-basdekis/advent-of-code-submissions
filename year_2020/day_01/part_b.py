#!/usr/bin/env python3
import utils

from year_2020.day_01.part_a import binary_search, parse_entries


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        278064990
        """
        triplet = find_triplet_with_sum(parse_entries(_input), 2020)
        if not triplet:
            raise Exception("Could not find triplet")

        first, second, third = triplet

        return first * second * third


def find_triplet_with_sum(entries, desired_sum):
    """
    >>> find_triplet_with_sum([299, 366, 675, 979, 1456, 1721], 2020)
    (366, 675, 979)
    >>> find_triplet_with_sum([], 2020)
    """
    for first_index, first in enumerate(entries):
        for second_index, second in enumerate(entries[first_index + 1:]):
            relative_third_index = binary_search(
                entries[second_index + 1:], desired_sum,
                (first + second).__add__)
            if relative_third_index is not None:
                third_index = relative_third_index + second_index + 1
                third = entries[third_index]
                return first, second, third

    return None


Challenge.main()
challenge = Challenge()
