#!/usr/bin/env python3
import math

import utils

from year_2019.day_12.part_a import repeat


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '30550349'
        """
        return get_nth_phase_message(_input.strip())


def get_nth_phase_message(initial, count=100, message_offset=0):
    """
    >>> get_nth_phase_message('12345678', 4)
    '01029498'
    >>> get_nth_phase_message('80871224585914546619083218645595')
    '24176176'
    >>> get_nth_phase_message('19617804207202209144916044189917')
    '73745418'
    >>> get_nth_phase_message('69317163492948606335995924319873')
    '52432133'
    """
    if isinstance(initial, str):
        initial = list(map(int, initial))
    phase_patterns = list(get_phase_patterns(len(initial)))
    result = repeat(
        get_next_phase, count, initial,
        kwargs={'phase_patterns': phase_patterns})
    return "".join(map(str, result))[message_offset:message_offset + 8]


def get_next_phase(phase, phase_patterns=None):
    """
    >>> "".join(map(str, get_next_phase(list(map(int, '12345678')))))
    '48226158'
    >>> "".join(map(str, get_next_phase(list(map(int, '48226158')))))
    '34040438'
    >>> "".join(map(str, get_next_phase(list(map(int, '34040438')))))
    '03415518'
    >>> "".join(map(str, get_next_phase(list(map(int, '03415518')))))
    '01029498'
    """
    if phase_patterns is None:
        phase_patterns = get_phase_patterns(len(phase))
    return [
        get_element_for_next_phase(
            phase, index, phase_pattern=phase_pattern)
        for index, phase_pattern in zip(range(len(phase)), phase_patterns)
    ]


def get_phase_patterns(length):
    return (
        get_phase_pattern(position, length)
        for position in range(length)
    )


def get_element_for_next_phase(phase, position, phase_pattern=None):
    """
    >>> get_element_for_next_phase(list(map(int, '12345678')), 0)
    4
    """
    if phase_pattern is None:
        phase_pattern = get_phase_pattern(position, len(phase))
    return abs(sum(
        element * coefficient
        for element, coefficient in zip(phase, phase_pattern)
    )) % 10


def get_phase_pattern(position, length):
    """
    >>> get_phase_pattern(0, 1)
    [1]
    >>> get_phase_pattern(0, 4)
    [1, 0, -1, 0]
    >>> get_phase_pattern(0, 12)
    [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1, 0]
    >>> get_phase_pattern(2, 12)
    [0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0]
    """
    phase_base_pattern = get_phase_base_pattern(position)
    return (
        phase_base_pattern
        * math.ceil((length + 1) / len(phase_base_pattern))
    )[1:length + 1]


def get_phase_base_pattern(position):
    """
    >>> get_phase_base_pattern(0)
    [0, 1, 0, -1]
    >>> get_phase_base_pattern(1)
    [0, 0, 1, 1, 0, 0, -1, -1]
    >>> get_phase_base_pattern(2)
    [0, 0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1]
    """
    return (
        [0] * (position + 1)
        + [1] * (position + 1)
        + [0] * (position + 1)
        + [-1] * (position + 1)
    )


challenge = Challenge()
challenge.main()
