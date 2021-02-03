#!/usr/bin/env python3
import utils

from year_2019.day_02.part_a import get_program_result


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        8226
        """
        noun, verb = find_verb_and_noun(_input, 19690720)

        return 100 * noun + verb


def find_verb_and_noun(program_text, expected_value):
    """
    >>> _input = challenge.input
    >>> find_verb_and_noun(_input, 2890696)
    (12, 2)
    >>> find_verb_and_noun(_input, 19690720)
    (82, 26)
    """
    for noun in range(100):
        for verb in range(100):
            value = get_program_result(program_text, {1: noun, 2: verb})
            if value == expected_value:
                return noun, verb

    raise Exception(f"Could not find and noun to result in {expected_value}")


Challenge.main()
challenge = Challenge()
