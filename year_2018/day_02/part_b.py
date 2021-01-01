#!/usr/bin/env python3
import itertools

import utils

from year_2018.day_02.part_a import parse_boxes


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        'evsialkqyiurohzpwucngttmf'
        """
        replaced_and_pair = find_one_letter_difference_pair(parse_boxes(_input))
        if not replaced_and_pair:
            raise Exception("Could not find 1-letter difference pair")

        replaced, _ = replaced_and_pair

        return replaced.replace('!', '')


def find_one_letter_difference_pair(box_ids):
    """
    >>> find_one_letter_difference_pair(parse_boxes(
    ...     "abcde\\n"
    ...     "fghij\\n"
    ...     "klmno\\n"
    ...     "pqrst\\n"
    ...     "fguij\\n"
    ...     "axcye\\n"
    ...     "wvxyz\\n"
    ... ))
    ('fg!ij', ('fghij', 'fguij'))
    """
    one_letter_difference_groups = [
        (group[0][0], tuple(sorted(
            box_id
            for _, box_id in group
        )))
        for group in (
            tuple(group)
            for _, group in itertools.groupby(sorted(
                (box_id[:index] + "!" + box_id[index + 1:], box_id)
                for box_id in box_ids
                for index in range(len(box_id))
            ), key=lambda item: item[0])
        )
        if len(group) > 1
    ]
    if not one_letter_difference_groups:
        return None
    if len(one_letter_difference_groups) > 1:
        raise Exception(f"Found {len(one_letter_difference_groups)} groups")
    (replaced, group), = one_letter_difference_groups
    if not group:
        raise Exception("Group was empty")
    if len(group) > 2:
        raise Exception(f"Group had {len(group)} items: {group}")

    return replaced, group


challenge = Challenge()
challenge.main()
