#!/usr/bin/env python3
import doctest
import math

from utils import get_current_directory
from year_2019.day_12.part_a import repeat


def solve(_input=None):
    """
    >>> solve()
    '30550349'
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return repeat(get_next_phase, 100, _input.strip())[:8]


def get_next_phase(phase_text):
    """
    >>> get_next_phase('12345678')
    '48226158'
    >>> get_next_phase('48226158')
    '34040438'
    >>> get_next_phase('34040438')
    '03415518'
    >>> get_next_phase('03415518')
    '01029498'
    >>> repeat(get_next_phase, 100, '80871224585914546619083218645595')[:8]
    '24176176'
    >>> repeat(get_next_phase, 100, '19617804207202209144916044189917')[:8]
    '73745418'
    >>> repeat(get_next_phase, 100, '69317163492948606335995924319873')[:8]
    '52432133'
    """
    return "".join(map(str, (
        get_element_for_next_phase(phase_text, index)
        for index in range(len(phase_text))
    )))


def get_element_for_next_phase(phase_text, position):
    """
    >>> get_element_for_next_phase('12345678', 0)
    4
    """
    phase = list(map(int, phase_text))
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
    return sum([
        [0] * (position + 1),
        [1] * (position + 1),
        [0] * (position + 1),
        [-1] * (position + 1),
    ], [])


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
