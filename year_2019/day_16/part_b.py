#!/usr/bin/env python3
import math

import utils
from aox.challenge import Debugger

from year_2019.day_16.part_a import get_phase_patterns, get_next_phase, \
    get_nth_phase_message, get_digit


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        42
        """
        input_message = _input.strip()
        original_initial = input_message * 10000
        original_offset = int(input_message[:7])
        return get_nth_phase_message(
            original_initial, count=1, message_offset=original_offset,
            debugger=debugger,
        )

        # return "".join(map(str, (
        #     get_digit(original_initial, offset, count=2)
        #     for offset in range(original_offset, original_offset + 8)
        # )))

        # original_initial_length = len(input_message) * 10000
        # # original_initial = input_message * 10000
        # truncated_initial_length = (
        #     original_initial_length
        #     - (
        #         math.floor(original_offset / len(input_message))
        #         * len(input_message)
        #     )
        # )
        # debugger.report(f"Creating a message of {truncated_initial_length / 1000}K instead of {original_initial_length / 1000}K")
        # truncated_initial = (
        #     input_message
        #     * (truncated_initial_length // len(input_message))
        # )
        # truncated_offset = (
        #     original_offset
        #     - (original_initial_length - truncated_initial_length)
        # )
        # debugger.report(f"Offset will be {truncated_offset} instead of {original_offset}")
        # truncated_initial = list(map(int, truncated_initial))
        # debugger.report(f"Created a list of length {len(truncated_initial)}")
        # return get_nth_phase_message(
        #     truncated_initial,
        #     message_offset=truncated_offset,
        #     count=1,
        #     debugger=debugger,
        # )
        # return decode_signal(_input.strip())


def decode_signal(message):
    # """
    # >>> decode_signal('03')
    # '84462026'
    # """
    # """
    # >>> decode_signal('03036732577212944063491565474664')
    # '84462026'
    # >>> decode_signal('02935109699940807407585447034323')
    # '78725270'
    # >>> decode_signal('03081770884921959731165446850517')
    # '53553731'
    # """
    signal = message * 10000
    message_offset = int(signal[:7])
    return get_nth_phase_message_multiple(
        signal, message_offset=message_offset)


def get_nth_phase_message_multiple(initial, count=100, message_offset=0):
    """
    >>> get_nth_phase_message_multiple('12345678', 2)
    '34040438'
    >>> get_nth_phase_message_multiple('12345678', 4)
    '01029498'
    """
    """
    >>> get_nth_phase_message_multiple('80871224585914546619083218645595')
    '24176176'
    >>> get_nth_phase_message_multiple('19617804207202209144916044189917')
    '73745418'
    >>> get_nth_phase_message_multiple('69317163492948606335995924319873')
    '52432133'
    """
    if isinstance(initial, str):
        initial = list(map(int, initial))
    phase_patterns = multiple_phase_patterns(
        list(map(list, get_phase_patterns(len(initial)))), count)
    result = get_next_phase(initial, len(initial), phase_patterns)
    # phase_patterns = multiple_phase_patterns(
    #     list(get_phase_patterns(len(initial))), 2)
    # result = repeat(
    #     get_next_phase, count // 2, initial,
    #     kwargs={'phase_patterns': phase_patterns})
    return "".join(map(str, result))[message_offset:message_offset + 8]


def multiple_phase_patterns(patterns, count):
    """
    >>> single = list(map(list, get_phase_patterns(8)))
    >>> multiple_phase_patterns(single, 1) == single
    True
    >>> doubled = combine_phase_patterns(single, single)
    >>> multiple_phase_patterns(single, 2) == doubled
    True
    >>> quadrupled = combine_phase_patterns(doubled, doubled)
    >>> multiple_phase_patterns(single, 4) == quadrupled
    True
    >>> quadrupled_plus_doubled = combine_phase_patterns(quadrupled, doubled)
    >>> multiple_phase_patterns(single, 6) == quadrupled_plus_doubled
    True
    >>> combined_50 = multiple_phase_patterns(single, 50)
    >>> combined_50_twice = combine_phase_patterns(combined_50, combined_50)
    >>> multiple_phase_patterns(single, 100) == combined_50_twice
    True
    """
    powers_needed = get_powers_needed(count)
    max_power = powers_needed[-1]
    patterns_powers = [None] * (max_power + 1)
    patterns_powers[0] = patterns
    for power in range(1, max_power + 1):
        patterns_powers[power] = combine_phase_patterns(
            patterns_powers[power - 1], patterns_powers[power - 1])

    result = patterns_powers[-1]
    for power in powers_needed[:-1]:
        result = combine_phase_patterns(result, patterns_powers[power])

    return result


def get_powers_needed(count):
    """
    >>> get_powers_needed(1)
    [0]
    >>> get_powers_needed(2)
    [1]
    >>> get_powers_needed(3)
    [0, 1]
    >>> get_powers_needed(4)
    [2]
    >>> get_powers_needed(100)
    [2, 5, 6]
    """
    return list(
        power
        for power, include
        in enumerate(map(bool, map(int, reversed(format(count, 'b')))))
        if include
    )


def combine_phase_patterns(lhs, rhs):
    """
    >>> single = list(get_phase_patterns(8))
    >>> doubled = combine_phase_patterns(single, single)
    >>> doubled
    [[1, 0, -2, -1, 1, 1, -1, 0], \
[0, 1, 2, 1, 1, -2, -3, -2], \
[0, 0, 1, 2, 3, 2, 2, 1], \
[0, 0, 0, 1, 2, 3, 4, 3], \
[0, 0, 0, 0, 1, 2, 3, 4], \
[0, 0, 0, 0, 0, 1, 2, 3], \
[0, 0, 0, 0, 0, 0, 1, 2], \
[0, 0, 0, 0, 0, 0, 0, 1]]
    >>> doubled_twice = combine_phase_patterns(doubled, doubled)
    >>> quadrupled = combine_phase_patterns(combine_phase_patterns(\
        combine_phase_patterns(single, single), single), single)
    >>> doubled_twice == quadrupled
    True
    >>> quadrupled_plus_doubled = combine_phase_patterns(quadrupled, doubled)
    >>> doubled_plus_quadrupled = combine_phase_patterns(doubled, quadrupled)
    >>> sextupled = combine_phase_patterns(combine_phase_patterns(\
        combine_phase_patterns(combine_phase_patterns(combine_phase_patterns(\
        single, single), single), single), single), single)
    >>> quadrupled_plus_doubled == sextupled
    True
    """
    length = len(lhs)
    result = [[0] * length for _ in range(length)]
    for result_row, lhs_row in zip(result, lhs):
        for lhs_coefficient, rhs_row in zip(lhs_row, rhs):
            if not lhs_coefficient:
                continue
            for index, rhs_coefficient in zip(range(length), rhs_row):
                if not rhs_coefficient:
                    continue
                result_row[index] += lhs_coefficient * rhs_coefficient

    return result


Challenge.main()
challenge = Challenge()
