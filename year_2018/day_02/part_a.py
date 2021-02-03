#!/usr/bin/env python3
import itertools

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        6448
        """
        return get_boxes_checksum(parse_boxes(_input))


def get_boxes_checksum(box_ids):
    """
    >>> get_boxes_checksum(["abcdef"])
    0
    >>> get_boxes_checksum(["bababc"])
    1
    >>> get_boxes_checksum(["abbcde"])
    0
    >>> get_boxes_checksum(["abcccd"])
    0
    >>> get_boxes_checksum([
    ...     "abcdef",
    ...     "bababc",
    ...     "abbcde",
    ...     "abcccd",
    ...     "aabcdd",
    ...     "abcdee",
    ...     "ababab",
    ... ])
    12
    """
    count_2, count_3 = get_two_and_three_letter_instances_counts(box_ids)
    return count_2 * count_3


def get_two_and_three_letter_instances_counts(box_ids):
    """
    >>> get_two_and_three_letter_instances_counts(["abcdef"])
    (0, 0)
    >>> get_two_and_three_letter_instances_counts(["bababc"])
    (1, 1)
    >>> get_two_and_three_letter_instances_counts(["abbcde"])
    (1, 0)
    >>> get_two_and_three_letter_instances_counts(["abcccd"])
    (0, 1)
    >>> get_two_and_three_letter_instances_counts([
    ...     "abcdef",
    ...     "bababc",
    ...     "abbcde",
    ...     "abcccd",
    ...     "aabcdd",
    ...     "abcdee",
    ...     "ababab",
    ... ])
    (4, 3)
    """
    count_2, count_3 = 0, 0
    for box_id in box_ids:
        has_2, has_3 = get_two_and_three_letter_instances_presence(box_id)
        if has_2:
            count_2 += 1
        if has_3:
            count_3 += 1

    return count_2, count_3


def get_two_and_three_letter_instances_presence(box_id):
    """
    >>> get_two_and_three_letter_instances_presence("abcdef")
    (False, False)
    >>> get_two_and_three_letter_instances_presence("bababc")
    (True, True)
    >>> get_two_and_three_letter_instances_presence("abbcde")
    (True, False)
    >>> get_two_and_three_letter_instances_presence("abcccd")
    (False, True)
    >>> get_two_and_three_letter_instances_presence("aabcdd")
    (True, False)
    >>> get_two_and_three_letter_instances_presence("abcdee")
    (True, False)
    >>> get_two_and_three_letter_instances_presence("ababab")
    (False, True)
    """
    counts_present = {
        count
        for count in (
            len(tuple(letters))
            for _, letters in itertools.groupby(sorted(box_id))
        )
        if count in (2, 3)
    }

    return 2 in counts_present, 3 in counts_present


def parse_boxes(boxes_text):
    """
    >>> parse_boxes("abc\\ncde\\n")
    ['abc', 'cde']
    >>> parse_boxes(
    ...     "evsialkqydurohxqpwbcugtjmh\\n"
    ...     "evsialkqydurohxzssbcngtjmv\\n"
    ...     "fvlialkqydurohxzpwbcngujmf\\n"
    ... )
    ['evsialkqydurohxqpwbcugtjmh', 'evsialkqydurohxzssbcngtjmv', 'fvlialkqydurohxzpwbcngujmf']
    """
    lines = boxes_text.splitlines()
    non_empty_lines = filter(None, lines)
    return list(non_empty_lines)


Challenge.main()
challenge = Challenge()
