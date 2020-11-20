#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_02.part_a import parse_program, serialise_program


def solve(_input=None):
    """
    >>> solve()
    12234644
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _, output_stream = get_program_result_and_output(_input, [1])

    *test_outputs, diagnostic_code = output_stream
    if not test_outputs:
        raise Exception("No test codes returned")
    if any(test_outputs):
        raise Exception(f"Some tests failed: {test_outputs}")
    return diagnostic_code


def get_program_result_and_output(program_text, input_stream,
                                  substitutions=None):
    if substitutions:
        program = parse_program(program_text)
        for position, substitution in substitutions.items():
            program[position] = substitution
        program_text = serialise_program(program)
    result_text, output_stream = \
        run_program_extended(program_text, input_stream)
    result = parse_program(result_text)
    return result[0], output_stream


def run_program_extended(program_text, input_stream):
    """
    >>> run_program_extended("1,9,10,3,2,3,11,0,99,30,40,50", [])
    ('3500,9,10,70,2,3,11,0,99,30,40,50', [])
    >>> run_program_extended("1,0,0,0,99", [])
    ('2,0,0,0,99', [])
    >>> run_program_extended("2,3,0,3,99", [])
    ('2,3,0,6,99', [])
    >>> run_program_extended("2,4,4,5,99,0", [])
    ('2,4,4,5,99,9801', [])
    >>> run_program_extended("1,1,1,4,99,5,6,0,99", [])
    ('30,1,1,4,2,5,6,0,99', [])
    >>> run_program_extended("1002,4,3,4,33", [])
    ('1002,4,3,4,99', [])
    >>> run_program_extended("1101,100,-1,4,0", [])
    ('1101,100,-1,4,99', [])
    >>> run_program_extended("3,0,99", [1])
    ('1,0,99', [])
    >>> run_program_extended("4,0,99", [1])
    ('4,0,99', [4])
    >>> run_program_extended("3,5,4,5,99,255", [60])
    ('3,5,4,5,99,60', [60])
    >>> run_program_extended("3,2,255,7,8,9,99,4,5,255", [1])
    ('3,2,1,7,8,9,99,4,5,9', [])
    >>> run_program_extended("3,2,255,7,8,9,99,4,5,255", [2])
    ('3,2,2,7,8,9,99,4,5,20', [])
    """
    program = parse_program(program_text)
    program_counter = 0
    input_stream_counter = 0
    output_stream = []
    while True:
        parameter_modes, op_code = break_down_op_code(program[program_counter])
        if op_code == 99:
            break
        if op_code not in OP_HANDLERS:
            raise Exception(f"Unknown op code {op_code}")
        handler = OP_HANDLERS[op_code]
        program_counter, input_stream_counter = handler(
            parameter_modes, program, program_counter, input_stream,
            input_stream_counter, output_stream)

    return serialise_program(program), output_stream


def break_down_op_code(full_op_code):
    """
    >>> break_down_op_code(99)
    ('', 99)
    >>> break_down_op_code(1)
    ('', 1)
    >>> break_down_op_code(1001)
    ('10', 1)
    >>> break_down_op_code(11101)
    ('111', 1)
    >>> break_down_op_code(3)
    ('', 3)
    """
    parameter_modes, op_code = \
        str(full_op_code)[:-2], int(str(full_op_code)[-2:])

    return parameter_modes, op_code


MODE_POSITION = '0'
MODE_IMMEDIATE = '1'


def handle_addition(parameter_modes, program, program_counter,
                    input_stream, input_stream_counter, output_stream):
    program_counter += 1
    (_, _, pointer_3), (value_1, value_2, _), program_counter = get_values(
        3, parameter_modes, program, program_counter,
        force_parameter_modes={2: MODE_POSITION})

    program[pointer_3] = value_1 + value_2

    return program_counter, input_stream_counter


def handle_multiplication(parameter_modes, program, program_counter,
                          input_stream, input_stream_counter, output_stream):
    """
    >>> program_a = [1, 5, 6, 7, 99, 10, 11, 12]
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('', _program, 0, [], 0, [])
    ([1, 5, 6, 7, 99, 10, 11, 110], (4, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('000', _program, 0, [], 0, [])
    ([1, 5, 6, 7, 99, 10, 11, 110], (4, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('1', _program, 0, [], 0, [])
    ([1, 5, 6, 7, 99, 10, 11, 55], (4, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('001', _program, 0, [], 0, [])
    ([1, 5, 6, 7, 99, 10, 11, 55], (4, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('10', _program, 0, [], 0, [])
    ([1, 5, 6, 7, 99, 10, 11, 60], (4, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('010', _program, 0, [], 0, [])
    ([1, 5, 6, 7, 99, 10, 11, 60], (4, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('111', _program, 0, [], 0, [])
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be '0' but was '1'
    >>> _program = list(program_a); _program, handle_multiplication('100', _program, 0, [], 0, [])
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be '0' but was '1'
    """
    program_counter += 1
    (_, _, pointer_3), (value_1, value_2, _), program_counter = get_values(
        3, parameter_modes, program, program_counter,
        force_parameter_modes={2: MODE_POSITION})

    program[pointer_3] = value_1 * value_2

    return program_counter, input_stream_counter


def handle_input(parameter_modes, program, program_counter, input_stream,
                 input_stream_counter, output_stream):
    """
    >>> _program = [3, 0]; _program, handle_input("", _program, 0, [1], 0, [])
    ([1, 0], (2, 1))
    """
    program_counter += 1
    (pointer_1, ), _, program_counter = get_values(
        1, parameter_modes, program, program_counter,
        force_parameter_modes={0: MODE_POSITION})

    program[pointer_1] = input_stream[input_stream_counter]
    input_stream_counter += 1

    return program_counter, input_stream_counter


def handle_output(parameter_modes, program, program_counter, input_stream,
                  input_stream_counter, output_stream):
    program_counter += 1
    _, (value_1,), program_counter = get_values(
        1, parameter_modes, program, program_counter)

    output_stream.append(value_1)

    return program_counter, input_stream_counter


def get_values(count, parameter_modes, program, program_counter,
               force_parameter_modes=None):
    """
    >>> get_values(3, '', [1, 5, 6, 7, 99, 10, 11, 12], 1)
    ([5, 6, 7], [10, 11, 12], 4)
    >>> get_values(3, '000', [1, 5, 6, 7, 99, 10, 11, 12], 1)
    ([5, 6, 7], [10, 11, 12], 4)
    >>> get_values(3, '1', [1, 5, 6, 7, 99, 10, 11, 12], 1)
    ([None, 6, 7], [5, 11, 12], 4)
    >>> get_values(3, '001', [1, 5, 6, 7, 99, 10, 11, 12], 1)
    ([None, 6, 7], [5, 11, 12], 4)
    >>> get_values(3, '10', [1, 5, 6, 7, 99, 10, 11, 12], 1)
    ([5, None, 7], [10, 6, 12], 4)
    >>> get_values(3, '010', [1, 5, 6, 7, 99, 10, 11, 12], 1)
    ([5, None, 7], [10, 6, 12], 4)
    >>> get_values(3, '111', [1, 5, 6, 7, 99, 10, 11, 12], 1)
    ([None, None, None], [5, 6, 7], 4)
    >>> get_values(3, '111', [1, 5, 6, 7, 99, 10, 11, 12], 1, \
                   {2: MODE_POSITION})
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be '0' but was '1'
    >>> get_values(3, '100', [1, 5, 6, 7, 99, 10, 11, 12], 1, \
                   {2: MODE_POSITION})
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be '0' but was '1'
    """
    parameter_modes = parameter_modes.rjust(count, "0")
    pointers_or_values = \
        program[program_counter:program_counter + count]
    pointers = [None] * count
    values = [None] * count
    for index, (parameter_mode, pointer_or_value) \
            in enumerate(zip(reversed(parameter_modes), pointers_or_values)):
        if force_parameter_modes and index in force_parameter_modes:
            forced_parameter_mode = force_parameter_modes[index]
            if parameter_mode != forced_parameter_mode:
                raise Exception(
                    f"Expected parameter {index} mode to be "
                    f"'{forced_parameter_mode}' but was '{parameter_mode}'")
        if parameter_mode == MODE_POSITION:
            pointer = pointer_or_value
            value = program[pointer]
        else:
            pointer = None
            value = pointer_or_value
        pointers[index] = pointer
        values[index] = value

    program_counter += count
    return pointers, values, program_counter


OP_HANDLERS = {
    1: handle_addition,
    2: handle_multiplication,
    3: handle_input,
    4: handle_output,
}


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
