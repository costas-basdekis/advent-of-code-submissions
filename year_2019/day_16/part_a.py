#!/usr/bin/env python3
import numpy as np
from itertools import zip_longest, islice
from typing import Iterable, Optional, Union, List, Dict, Tuple

import utils
from aox.challenge import Debugger
from utils import cached


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        '30550349'
        """
        return get_nth_phase_message(_input.strip())


def get_digit(
    initial: Union[str, List[int]], position: int, count: int = 100,
    cache: Optional[Dict[Tuple[int, int], int]] = None,
) -> int:
    if count == 0:
        return int(initial[position % len(initial)])
    key = (position, count)
    if cache is None or key not in cache:
        value = abs(sum(
            get_digit(initial, next_position, count=count - 1, cache=cache)
            * coef
            for next_position, coef
            in enumerate(get_phase_pattern(position, len(initial)))
            # if coef
        )) % 10
        if cache is not None:
            cache[key] = value
    else:
        value = cache[key]
    return value


def get_nth_phase_message(
    initial: Union[str, Iterable[int]], length: Optional[int] = None,
    count: int = 100, message_offset: int = 0,
    debugger: Debugger = Debugger(enabled=False),
) -> str:
    """
    >>> get_nth_phase_message('12345678', count=4)
    '01029498'
    >>> get_nth_phase_message('80871224585914546619083218645595')
    '24176176'
    >>> get_nth_phase_message('19617804207202209144916044189917')
    '73745418'
    >>> get_nth_phase_message('69317163492948606335995924319873')
    '52432133'
    """
    if length is None:
        if not hasattr(initial, '__str__'):
            raise Exception(
                f"Initial has no length capability, and no length was passed"
            )
        length = len(initial)
    if isinstance(initial, str):
        initial = list(map(int, initial))
    result = np.array(initial)
    # phase_patterns = list(map(list, get_phase_patterns(length)))
    debugger.default_report(f"Doing {count} iterations")
    for iteration in debugger.stepping(range(1, count + 1)):
        result = get_next_phase(result, length, debugger=debugger)
        debugger.default_report_if(f"Done {iteration}/{count}")
    return "".join(map(str, result[message_offset:message_offset + 8]))


def get_next_phase(
    phase: np.ndarray, length: int,
    phase_patterns: Optional[List[np.ndarray]] = None,
    debugger: Debugger = Debugger(enabled=False),
) -> List[int]:
    """
    >>> "".join(map(str, get_next_phase(np.array(list(map(int, '12345678'))), 8)))
    '48226158'
    >>> "".join(map(str, get_next_phase(np.array(list(map(int, '48226158'))), 8)))
    '34040438'
    >>> "".join(map(str, get_next_phase(np.array(list(map(int, '34040438'))), 8)))
    '03415518'
    >>> "".join(map(str, get_next_phase(np.array(list(map(int, '03415518'))), 8)))
    '01029498'
    """
    # if phase_patterns is None:
    #     phase_patterns = get_phase_patterns(length)
    if phase_patterns is None:
        indexes_and_phase_patterns = zip_longest(
            range(length), [], fillvalue=None,
        )
    else:
        indexes_and_phase_patterns = enumerate(phase_patterns)

    next_phase = []
    for index, phase_pattern in debugger.stepping(indexes_and_phase_patterns):
        next_phase.append(get_element_for_next_phase(
            phase, length, index, phase_pattern=phase_pattern))
        debugger.default_report_if(
            f"{index}/{length} ({index * 100 // length}%)"
        )

    return next_phase


def get_phase_patterns(length: int) -> List[np.ndarray]:
    return [
        get_phase_pattern(position, length)
        for position in range(length)
    ]


def get_element_for_next_phase(
    phase: np.ndarray, length: int, position: int,
    phase_pattern: Optional[np.ndarray] = None,
) -> int:
    """
    >>> get_element_for_next_phase(np.array(list(map(int, '12345678'))), 8, 0)
    4
    """
    if phase_pattern is None:
        # return abs(sum(
        #     value * get_coefficient(position, index)
        #     for index, value in enumerate(phase)
        # )) % 10
        phase_pattern = get_phase_pattern(position, length)
    return abs(phase_pattern.dot(phase)) % 10


@cached
def get_phase_pattern(position: int, length: int) -> np.ndarray:
    """
    >>> list(get_phase_pattern(0, 1))
    [1]
    >>> list(get_phase_pattern(0, 4))
    [1, 0, -1, 0]
    >>> list(get_phase_pattern(0, 12))
    [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1, 0]
    >>> list(get_phase_pattern(2, 12))
    [0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0]
    """
    def get_infinite_pattern() -> Iterable[int]:
        while True:
            yield from get_phase_base_pattern(position)

    infinite_pattern = iter(get_infinite_pattern())
    next(infinite_pattern)

    return np.array(list(islice(infinite_pattern, length)))


def get_phase_base_pattern(position: int) -> Iterable[int]:
    """
    >>> list(get_phase_base_pattern(0))
    [0, 1, 0, -1]
    >>> list(get_phase_base_pattern(1))
    [0, 0, 1, 1, 0, 0, -1, -1]
    >>> list(get_phase_base_pattern(2))
    [0, 0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1]
    """
    for coef in (0, 1, 0, -1):
        for _ in range(position + 1):
            yield coef


COEFFICIENTS_PATTERN = (0, 1, 0, -1)


def get_coefficient(position: int, index: int) -> int:
    """
    >>> # noinspection PyUnresolvedReferences
    >>> [get_coefficient(0, _index) for _index in range(12)]
    [1, 0, -1, 0, 1, 0, -1, 0, 1, 0, -1, 0]
    >>> # noinspection PyUnresolvedReferences
    >>> [get_coefficient(2, _index) for _index in range(12)]
    [0, 0, 1, 1, 1, 0, 0, 0, -1, -1, -1, 0]
    """
    offset_index = index + 1
    portion_length = position + 1
    pattern_length = portion_length * 4
    modulo_index = offset_index % pattern_length
    portion_index = modulo_index // portion_length
    return COEFFICIENTS_PATTERN[portion_index]


Challenge.main()
challenge = Challenge()
