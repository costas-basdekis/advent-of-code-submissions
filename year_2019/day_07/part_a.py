#!/usr/bin/env python3
import doctest
import itertools

from utils import get_current_directory
from year_2019.day_05.part_a import InsufficientInputError
from year_2019.day_05.part_b import get_program_result_and_output_extended


def solve(_input=None):
    """
    >>> solve()
    368584
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return get_max_amplifier_chain_result(_input)


def get_max_amplifier_chain_result(program_text, phase_inputs=tuple(range(5)),
                                   initial_input=0):
    """
    >>> get_max_amplifier_chain_result(\
        '3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0')
    43210
    >>> get_max_amplifier_chain_result(\
        '3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99'\
        ',0,0')
    54321
    >>> get_max_amplifier_chain_result(\
        '3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33'\
        ',31,31,1,32,31,31,4,31,99,0,0,0')
    65210
    """
    phase_sequences = itertools.permutations(phase_inputs)
    return max(
        get_amplifier_chain_result(program_text, phase_sequence, initial_input)
        for phase_sequence in phase_sequences
    )


def get_amplifier_chain_result(program_text, phase_sequence, initial_input=0):
    """
    >>> get_amplifier_chain_result(\
        '3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0', [4, 3, 2, 1, 0])
    43210
    >>> get_amplifier_chain_result(\
        '3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99'\
        ',0,0', [0, 1, 2, 3, 4])
    54321
    >>> get_amplifier_chain_result(\
        '3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33'\
        ',31,31,1,32,31,31,4,31,99,0,0,0', [1, 0, 4, 3, 2])
    65210
    """
    keep_looping = True
    inputs = [
        [phase]
        for phase in phase_sequence
    ]
    errors = [
        None
        for _ in phase_sequence
    ]
    value = initial_input
    while keep_looping:
        keep_looping = False
        for index, (error, _input) in enumerate(zip(errors, inputs)):
            _input.append(value)
            try:
                _, (value,) = get_program_result_and_output_extended(
                    program_text, _input, error=error)
                errors[index] = None
            except InsufficientInputError as e:
                errors[index] = e
                value = e.output_stream[-1]
                keep_looping = True

    return value


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
