#!/usr/bin/env python3
from typing import List

from itertools import islice

import math

import utils
from aox.challenge import Debugger


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        62938399
        """
        return get_message_after_index(_input.strip(), debugger=debugger)


def get_message_after_index(
    initial: str, debugger: Debugger = Debugger(enabled=False),
) -> str:
    """
    >>> get_message_after_index("03036732577212944063491565474664")
    84462026
    """
    start_index = int(initial[:7])
    original_length = len(initial)
    length = original_length * 10000
    skip_lengths_count = math.floor(start_index / original_length)
    lengths_count = int(length / original_length - skip_lengths_count)
    skipped_phase = list(map(int, initial)) * lengths_count
    skipped_offset = start_index - skip_lengths_count * original_length
    skipped_phase = skipped_phase[skipped_offset:]
    result = skipped_phase
    debugger.default_report(f"Looking for message skipping {start_index}")
    for _ in debugger.stepping(range(100)):
        result = get_next_phase_after_index(result, start_index)
        debugger.default_report_if(f"So far: {''.join(map(str, result[:8]))}")
    return "".join(map(str, result[:8]))


def get_next_phase_after_index(phase: List[int], start_index: int) -> List[int]:
    next_phase = []
    previous_item = sum(islice(phase, start_index)) % 10
    next_phase.append(previous_item)
    for position in range(start_index + 1, start_index + len(phase)):
        item = previous_item
        item -= phase[position - start_index - 1]
        item += sum(phase[2 * position - start_index:2 * position - start_index + 2])
        item %= 10
        next_phase.append(item)
        previous_item = item

    return next_phase


Challenge.main()
challenge = Challenge()
