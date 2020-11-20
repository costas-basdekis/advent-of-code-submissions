#!/usr/bin/env python3
import doctest

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    2890696
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return get_program_result(_input, {1: 12, 2: 2})


def get_program_result(program_text, substitutions=None):
    if substitutions:
        program = parse_program(program_text)
        for position, substitution in substitutions.items():
            program[position] = substitution
        program_text = serialise_program(program)
    result_text = run_program(program_text)
    result = parse_program(result_text)
    return result[0]


def run_program(program_text):
    """
    >>> run_program("1,9,10,3,2,3,11,0,99,30,40,50")
    '3500,9,10,70,2,3,11,0,99,30,40,50'
    >>> run_program("1,0,0,0,99")
    '2,0,0,0,99'
    >>> run_program("2,3,0,3,99")
    '2,3,0,6,99'
    >>> run_program("2,4,4,5,99,0")
    '2,4,4,5,99,9801'
    >>> run_program("1,1,1,4,99,5,6,0,99")
    '30,1,1,4,2,5,6,0,99'
    """
    program = parse_program(program_text)
    program_counter = 0
    while True:
        op_code = program[program_counter]
        if op_code == 99:
            break
        if op_code not in (1, 2):
            raise Exception(f"Unknown op code {op_code}")
        pointer_1, pointer_2, pointer_3 = \
            program[program_counter + 1:program_counter + 4]
        program_counter += 4
        value_1, value_2 = program[pointer_1], program[pointer_2]

        if op_code == 1:
            result = value_1 + value_2
        elif op_code == 2:
            result = value_1 * value_2
        else:
            raise Exception(f"Unknown op code {op_code}")

        program[pointer_3] = result

    return serialise_program(program)


def parse_program(program_text):
    return list(map(int, program_text.split(",")))


def serialise_program(program):
    return ",".join(map(str, program))


if __name__ == '__main__':
    doctest.testmod()
    print("Tests passed")
    print("Solution:", solve())
