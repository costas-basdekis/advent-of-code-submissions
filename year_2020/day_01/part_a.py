#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1019371
        """
        pair = find_pair_with_sum(parse_entries(_input), 2020)
        if not pair:
            raise Exception("Could not find pair")

        first, second = pair

        return first * second


def find_pair_with_sum(entries, desired_sum):
    """
    >>> find_pair_with_sum([299, 366, 675, 979, 1456, 1721], 2020)
    (299, 1721)
    >>> find_pair_with_sum([0, 366, 675, 979, 1456, 2020, 3000], 2020)
    (0, 2020)
    >>> find_pair_with_sum([], 2020)
    """
    for first_index, first in enumerate(entries):
        relative_second_index = binary_search(
            entries[first_index + 1:], desired_sum, first.__add__)
        if relative_second_index is not None:
            second_index = relative_second_index + first_index + 1
            second = entries[second_index]
            return first, second

    return None


def binary_search(items, target, value_func=lambda _item: _item):
    """
    >>> binary_search([], 5)
    >>> binary_search([1, 5, 9], 5)
    1
    >>> binary_search([1, 2, 3], 1, lambda _item: 1 + (_item - 1) * 4)
    0
    >>> binary_search([1, 2, 3], 5, lambda _item: 1 + (_item - 1) * 4)
    1
    >>> binary_search([1, 2, 3], 9, lambda _item: 1 + (_item - 1) * 4)
    2
    >>> binary_search([1, 2, 3], 2, lambda _item: 1 + (_item - 1) * 4)
    """
    if not items:
        return None

    lower_index = 0
    lower_item = value_func(items[lower_index])
    if lower_item == target:
        return lower_index
    elif lower_item > target:
        return None

    upper_index = len(items)
    upper_item = value_func(items[upper_index - 1])
    if upper_item == target:
        return upper_index - 1
    elif upper_item < target:
        return None

    while lower_index < upper_index:
        middle_index = lower_index + (upper_index - lower_index) // 2
        item = value_func(items[middle_index])
        if target == item:
            return middle_index
        elif target > item:
            if lower_index == middle_index:
                break
            lower_index = middle_index
        elif target < item:
            upper_index = middle_index


def parse_entries(entries_text):
    """
    >>> parse_entries(
    ...     "1721\\n"
    ...     "979\\n"
    ...     "366\\n"
    ...     "299\\n"
    ...     "675\\n"
    ...     "1456\\n"
    ... )
    [299, 366, 675, 979, 1456, 1721]
    """
    lines = entries_text.splitlines()
    non_empty_lines = filter(None, lines)
    return sorted(map(int, non_empty_lines))


Challenge.main()
challenge = Challenge()
