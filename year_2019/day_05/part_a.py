#!/usr/bin/env python3
import utils
from year_2019.day_02.part_a import parse_program, serialise_program


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        12234644
        """
        _, output_stream = get_program_result_and_output(_input, [1])

        *test_outputs, diagnostic_code = output_stream
        if not test_outputs:
            raise Exception("No test codes returned")
        if any(test_outputs):
            raise Exception(f"Some tests failed: {test_outputs}")
        return diagnostic_code


OP_HANDLERS = {}


def register_op_handler(op_code, override=False):
    def decorator(func):
        if not override and op_code in OP_HANDLERS:
            raise Exception(
                f"Op code '{op_code}' was already present, and "
                f"`override=False`")
        OP_HANDLERS[op_code] = func
        return func

    return decorator


# noinspection PyDefaultArgument
def get_program_result_and_output(program_text, input_stream,
                                  substitutions=None, op_handlers=OP_HANDLERS,
                                  error=None):
    if substitutions:
        program = parse_program(program_text)
        for position, substitution in substitutions.items():
            program[position] = substitution
        program_text = serialise_program(program)
    result_text, output_stream = \
        run_program_extended(
            program_text, input_stream, op_handlers=op_handlers, error=error)
    result = parse_program(result_text)
    return result[0], output_stream


# noinspection PyDefaultArgument
def run_program_extended(program_text, input_stream, op_handlers=OP_HANDLERS,
                         error=None):
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
    if error:
        program = error.program
        program_counter = error.program_counter
        input_stream_counter = error.input_stream_counter
        relative_base = error.relative_base
    else:
        program = parse_program(program_text)
        program_counter = 0
        input_stream_counter = 0
        relative_base = 0
    output_stream = []
    while True:
        parameter_modes, op_code = break_down_op_code(program[program_counter])
        if op_code == 99:
            break
        if op_code not in op_handlers:
            raise Exception(f"Unknown op code {op_code}")
        handler = op_handlers[op_code]
        program_counter, input_stream_counter, relative_base = handler(
            parameter_modes, program, program_counter, input_stream,
            input_stream_counter, output_stream, relative_base)

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
    >>> break_down_op_code(109)
    ('1', 9)
    """
    parameter_modes, op_code = \
        str(full_op_code)[:-2], int(str(full_op_code)[-2:])

    return parameter_modes, op_code


MODE_POSITION = '0'
MODE_IMMEDIATE = '1'
MODE_RELATIVE = '2'


@register_op_handler(1)
def handle_addition(parameter_modes, program, program_counter,
                    input_stream, input_stream_counter, output_stream,
                    relative_base):
    program_counter += 1
    (_, _, pointer_3), (value_1, value_2, _), program, program_counter = \
        get_values(
            3, parameter_modes, program, program_counter, relative_base,
            force_parameter_modes={2: [MODE_POSITION, MODE_RELATIVE]})

    program[pointer_3] = value_1 + value_2

    return program_counter, input_stream_counter, relative_base


@register_op_handler(2)
def handle_multiplication(parameter_modes, program, program_counter,
                          input_stream, input_stream_counter, output_stream,
                          relative_base):
    """
    >>> program_a = [2, 5, 6, 7, 99, 10, 11, 12]
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 110], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('2', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 110], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('2', _program, 0, [], 0, [], 2)
    ([2, 5, 6, 7, 99, 10, 11, 132], (4, 0, 2))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('000', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 110], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('1', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 55], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('001', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 55], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('10', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 60], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('010', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 60], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('010', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 60], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('012', _program, 0, [], 0, [], 0)
    ([2, 5, 6, 7, 99, 10, 11, 60], (4, 0, 0))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('012', _program, 0, [], 0, [], 2)
    ([2, 5, 6, 7, 99, 10, 11, 72], (4, 0, 2))
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('111', _program, 0, [], 0, [], 0)
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be one of 0, 2 but was '1'
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('100', _program, 0, [], 0, [], 0)
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be one of 0, 2 but was '1'
    >>> _program = list(program_a)
    >>> _program, handle_multiplication('3', _program, 0, [], 0, [], 0)
    Traceback (most recent call last):
    ...
    Exception: Unknown parameter mode '3'
    """
    program_counter += 1
    (_, _, pointer_3), (value_1, value_2, _), program, program_counter = \
        get_values(
            3, parameter_modes, program, program_counter, relative_base,
            force_parameter_modes={2: [MODE_POSITION, MODE_RELATIVE]})

    program[pointer_3] = value_1 * value_2

    return program_counter, input_stream_counter, relative_base


class InsufficientInputError(Exception):
    def __init__(self, program, program_counter, input_stream,
                 input_stream_counter, output_stream, relative_base):
        super().__init__("Insufficient input")
        self.program = program
        self.program_counter = program_counter
        self.input_stream = input_stream
        self.input_stream_counter = input_stream_counter
        self.output_stream = output_stream
        self.relative_base = relative_base


@register_op_handler(3)
def handle_input(parameter_modes, program, program_counter, input_stream,
                 input_stream_counter, output_stream, relative_base):
    """
    >>> _program = [3, 0]
    >>> _program, handle_input("", _program, 0, [1], 0, [], 0)
    ([1, 0], (2, 1, 0))
    """
    error = InsufficientInputError(
        program, program_counter, input_stream, input_stream_counter,
        output_stream, relative_base)
    program_counter += 1
    (pointer_1, ), _, program, program_counter = get_values(
        1, parameter_modes, program, program_counter, relative_base,
        force_parameter_modes={0: [MODE_POSITION, MODE_RELATIVE]})

    if input_stream_counter >= len(input_stream):
        raise error

    program[pointer_1] = input_stream[input_stream_counter]
    input_stream_counter += 1

    return program_counter, input_stream_counter, relative_base


@register_op_handler(4)
def handle_output(parameter_modes, program, program_counter, input_stream,
                  input_stream_counter, output_stream, relative_base):
    program_counter += 1
    _, (value_1,), program, program_counter = get_values(
        1, parameter_modes, program, program_counter, relative_base)

    output_stream.append(value_1)

    return program_counter, input_stream_counter, relative_base


def get_values(count, parameter_modes, program, program_counter, relative_base,
               force_parameter_modes=None):
    """
    >>> get_values(3, '', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0)
    ([5, 6, 7], [10, 11, 12], [1, 5, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '000', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0)
    ([5, 6, 7], [10, 11, 12], [1, 5, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '2', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0)
    ([5, 6, 7], [10, 11, 12], [1, 5, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '2', [1, 3, 6, 7, 99, 10, 11, 12], 1, 2)
    ([5, 6, 7], [10, 11, 12], [1, 3, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '1', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0)
    ([None, 6, 7], [5, 11, 12], [1, 5, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '001', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0)
    ([None, 6, 7], [5, 11, 12], [1, 5, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '10', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0)
    ([5, None, 7], [10, 6, 12], [1, 5, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '010', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0)
    ([5, None, 7], [10, 6, 12], [1, 5, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '111', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0)
    ([None, None, None], [5, 6, 7], [1, 5, 6, 7, 99, 10, 11, 12], 4)
    >>> get_values(3, '111', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0,\
                   {2: MODE_POSITION})
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be one of 0 but was '1'
    >>> get_values(3, '100', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0, \
                   {2: MODE_POSITION})
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be one of 0 but was '1'
    >>> get_values(3, '100', [1, 5, 6, 7, 99, 10, 11, 12], 1, 0, \
                   {2: [MODE_POSITION, MODE_RELATIVE]})
    Traceback (most recent call last):
    ...
    Exception: Expected parameter 2 mode to be one of 0, 2 but was '1'
    """
    parameter_modes = parameter_modes.rjust(count, MODE_POSITION)
    pointers_or_values = \
        program[program_counter:program_counter + count]
    pointers = [None] * count
    values = [None] * count
    for index, (parameter_mode, pointer_or_value_or_offset) \
            in enumerate(zip(reversed(parameter_modes), pointers_or_values)):
        if force_parameter_modes and index in force_parameter_modes:
            forced_parameter_mode_or_modes = force_parameter_modes[index]
            if isinstance(forced_parameter_mode_or_modes, str):
                forced_parameter_mode = forced_parameter_mode_or_modes
                forced_parameter_modes = [forced_parameter_mode]
            else:
                forced_parameter_modes = forced_parameter_mode_or_modes
            if parameter_mode not in forced_parameter_modes:
                raise Exception(
                    f"Expected parameter {index} mode to be one of "
                    f"{', '.join(forced_parameter_modes)} but was '{parameter_mode}'")
        if parameter_mode == MODE_POSITION:
            pointer = pointer_or_value_or_offset
            if pointer >= len(program):
                program += [0] * (pointer - len(program) + 1)
            value = program[pointer]
        elif parameter_mode == MODE_IMMEDIATE:
            pointer = None
            value = pointer_or_value_or_offset
        elif parameter_mode == MODE_RELATIVE:
            offset = pointer_or_value_or_offset
            pointer = relative_base + offset
            if pointer >= len(program):
                program += [0] * (pointer - len(program) + 1)
            value = program[pointer]
        else:
            raise Exception(f"Unknown parameter mode '{parameter_mode}'")
        pointers[index] = pointer
        values[index] = value

    program_counter += count
    return pointers, values, program, program_counter


challenge = Challenge()
challenge.main()
