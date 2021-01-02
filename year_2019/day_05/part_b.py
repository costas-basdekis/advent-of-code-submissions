#!/usr/bin/env python3
import utils

from year_2019.day_05.part_a import get_program_result_and_output, OP_HANDLERS,\
    get_values, MODE_POSITION, run_program_extended, MODE_RELATIVE


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3508186
        """
        _, output_stream = get_program_result_and_output_extended(_input, [5])

        *test_outputs, diagnostic_code = output_stream
        if test_outputs:
            raise Exception("Some test codes returned")
        if any(test_outputs):
            raise Exception(f"Some tests failed: {test_outputs}")
        return diagnostic_code


OP_HANDLERS_EXTENDED = dict(OP_HANDLERS)


def register_op_handler_extended(op_code, override=False):
    def decorator(func):
        if not override and op_code in OP_HANDLERS_EXTENDED:
            raise Exception(
                f"Op code '{op_code}' was already present, and "
                f"`override=False`")
        OP_HANDLERS_EXTENDED[op_code] = func
        return func

    return decorator


# noinspection PyDefaultArgument
def get_program_result_and_output_extended(
        program_text, input_stream, substitutions=None, error=None):
    """
    >>> def run_program_extended_doubly(*args, **kwargs):
    ...     return run_program_extended(
    ...         *args, **kwargs, op_handlers=OP_HANDLERS_EXTENDED)
    >>> run_program_extended_doubly("1,9,10,3,2,3,11,0,99,30,40,50", [])
    ('3500,9,10,70,2,3,11,0,99,30,40,50', [])
    >>> run_program_extended_doubly("1,0,0,0,99", [])
    ('2,0,0,0,99', [])
    >>> run_program_extended_doubly("2,3,0,3,99", [])
    ('2,3,0,6,99', [])
    >>> run_program_extended_doubly("2,4,4,5,99,0", [])
    ('2,4,4,5,99,9801', [])
    >>> run_program_extended_doubly("1,1,1,4,99,5,6,0,99", [])
    ('30,1,1,4,2,5,6,0,99', [])
    >>> run_program_extended_doubly("1002,4,3,4,33", [])
    ('1002,4,3,4,99', [])
    >>> run_program_extended_doubly("1101,100,-1,4,0", [])
    ('1101,100,-1,4,99', [])
    >>> run_program_extended_doubly("3,0,99", [1])
    ('1,0,99', [])
    >>> run_program_extended_doubly("4,0,99", [1])
    ('4,0,99', [4])
    >>> run_program_extended_doubly("3,5,4,5,99,255", [60])
    ('3,5,4,5,99,60', [60])
    >>> run_program_extended_doubly("3,2,255,7,8,9,99,4,5,255", [1])
    ('3,2,1,7,8,9,99,4,5,9', [])
    >>> run_program_extended_doubly("3,2,255,7,8,9,99,4,5,255", [2])
    ('3,2,2,7,8,9,99,4,5,20', [])
    >>> run_program_extended_doubly("5,4,5,99,0,6,4,0,99", [])
    ('5,4,5,99,0,6,4,0,99', [])
    >>> run_program_extended_doubly("5,4,5,99,1,6,4,0,99", [])
    ('5,4,5,99,1,6,4,0,99', [5])
    >>> run_program_extended_doubly("6,4,5,99,0,6,4,0,99", [])
    ('6,4,5,99,0,6,4,0,99', [6])
    >>> run_program_extended_doubly("6,4,5,99,1,6,4,0,99", [])
    ('6,4,5,99,1,6,4,0,99', [])
    >>> get_program_result_and_output_extended(\
        '3,9,8,9,10,9,4,9,99,-1,8', [7])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,9,8,9,10,9,4,9,99,-1,8', [8])[1]
    [1]
    >>> get_program_result_and_output_extended(\
        '3,9,8,9,10,9,4,9,99,-1,8', [9])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,3,1108,-1,8,3,4,3,99', [7])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,3,1108,-1,8,3,4,3,99', [8])[1]
    [1]
    >>> get_program_result_and_output_extended(\
        '3,3,1108,-1,8,3,4,3,99', [9])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,9,7,9,10,9,4,9,99,-1,8', [7])[1]
    [1]
    >>> get_program_result_and_output_extended(\
        '3,9,7,9,10,9,4,9,99,-1,8', [8])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,9,7,9,10,9,4,9,99,-1,8', [9])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,3,1107,-1,8,3,4,3,99', [7])[1]
    [1]
    >>> get_program_result_and_output_extended(\
        '3,3,1107,-1,8,3,4,3,99', [8])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,3,1107,-1,8,3,4,3,99', [9])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9', [0])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9', [2])[1]
    [1]
    >>> get_program_result_and_output_extended(\
        '3,3,1105,-1,9,1101,0,0,12,4,12,99,1', [0])[1]
    [0]
    >>> get_program_result_and_output_extended(\
        '3,3,1105,-1,9,1101,0,0,12,4,12,99,1', [2])[1]
    [1]
    >>> get_program_result_and_output_extended(\
        '3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0'\
        ',1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20'\
        ',1105,1,46,98,99', [7])[1]
    [999]
    >>> get_program_result_and_output_extended(\
        '3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0'\
        ',1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20'\
        ',1105,1,46,98,99', [8])[1]
    [1000]
    >>> get_program_result_and_output_extended(\
        '3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,1106,0,36,98,0,0'\
        ',1002,21,125,20,4,20,1105,1,46,104,999,1105,1,46,1101,1000,1,20,4,20'\
        ',1105,1,46,98,99', [9])[1]
    [1001]
    """
    return get_program_result_and_output(
        program_text, input_stream, substitutions=substitutions,
        op_handlers=OP_HANDLERS_EXTENDED, error=error)


@register_op_handler_extended(5)
def handle_jump_if_true(parameter_modes, program, program_counter,
                        input_stream, input_stream_counter, output_stream,
                        relative_base):
    """
    >>> handle_jump_if_true('11', [5, 0, 4, 99, 99], 0, [], 0, [], 0)
    (3, 0, 0)
    >>> handle_jump_if_true('11', [5, 1, 4, 99, 99], 0, [], 0, [], 0)
    (4, 0, 0)
    >>> handle_jump_if_true('', [5, 4, 5, 99, 0, 6, 99], 0, [], 0, [], 0)
    (3, 0, 0)
    >>> handle_jump_if_true('', [5, 4, 5, 99, 1, 6, 99], 0, [], 0, [], 0)
    (6, 0, 0)
    """
    program_counter += 1
    _, (value_1, value_2), program, program_counter = get_values(
        2, parameter_modes, program, program_counter, relative_base)

    if value_1:
        program_counter = value_2

    return program_counter, input_stream_counter, relative_base


@register_op_handler_extended(6)
def handle_jump_if_false(parameter_modes, program, program_counter,
                         input_stream, input_stream_counter, output_stream,
                         relative_base):
    """
    >>> handle_jump_if_false('11', [6, 0, 4, 99, 99], 0, [], 0, [], 0)
    (4, 0, 0)
    >>> handle_jump_if_false('11', [6, 1, 4, 99, 99], 0, [], 0, [], 0)
    (3, 0, 0)
    >>> handle_jump_if_false('', [6, 4, 5, 99, 0, 6, 99], 0, [], 0, [], 0)
    (6, 0, 0)
    >>> handle_jump_if_false('', [6, 4, 5, 99, 1, 6, 99], 0, [], 0, [], 0)
    (3, 0, 0)
    """
    program_counter += 1
    _, (value_1, value_2), program, program_counter = get_values(
        2, parameter_modes, program, program_counter, relative_base)

    if not value_1:
        program_counter = value_2

    return program_counter, input_stream_counter, relative_base


@register_op_handler_extended(7)
def handle_less_than(parameter_modes, program, program_counter,
                     input_stream, input_stream_counter, output_stream,
                     relative_base):
    """
    >>> _program = [7, 5, 6, 7, 99, 1, 2, 255]
    >>> _ = handle_less_than('', _program, 0, [], 0, [], 0)
    >>> _program
    [7, 5, 6, 7, 99, 1, 2, 1]
    >>> _program = [7, 5, 6, 7, 99, 2, 2, 255]
    >>> _ = handle_less_than('', _program, 0, [], 0, [], 0)
    >>> _program
    [7, 5, 6, 7, 99, 2, 2, 0]
    >>> _program = [7, 5, 6, 7, 99, 3, 2, 255]
    >>> _ = handle_less_than('', _program, 0, [], 0, [], 0)
    >>> _program
    [7, 5, 6, 7, 99, 3, 2, 0]
    """
    program_counter += 1
    (_, _, pointer_3), (value_1, value_2, _), program, program_counter = \
        get_values(
            3, parameter_modes, program, program_counter, relative_base,
            force_parameter_modes={2: [MODE_POSITION, MODE_RELATIVE]})

    if value_1 < value_2:
        program[pointer_3] = 1
    else:
        program[pointer_3] = 0

    return program_counter, input_stream_counter, relative_base


@register_op_handler_extended(8)
def handle_equal(parameter_modes, program, program_counter,
                 input_stream, input_stream_counter, output_stream,
                 relative_base):
    """
    >>> _program = [8, 5, 6, 7, 99, 1, 2, 255]
    >>> _ = handle_equal('', _program, 0, [], 0, [], 0)
    >>> _program
    [8, 5, 6, 7, 99, 1, 2, 0]
    >>> _program = [8, 5, 6, 7, 99, 2, 2, 255]
    >>> _ = handle_equal('', _program, 0, [], 0, [], 0)
    >>> _program
    [8, 5, 6, 7, 99, 2, 2, 1]
    >>> _program = [8, 5, 6, 7, 99, 3, 2, 255]
    >>> _ = handle_equal('', _program, 0, [], 0, [], 0)
    >>> _program
    [8, 5, 6, 7, 99, 3, 2, 0]
    """
    program_counter += 1
    (_, _, pointer_3), (value_1, value_2, _), program, program_counter = \
        get_values(
            3, parameter_modes, program, program_counter, relative_base,
            force_parameter_modes={2: [MODE_POSITION, MODE_RELATIVE]})

    if value_1 == value_2:
        program[pointer_3] = 1
    else:
        program[pointer_3] = 0

    return program_counter, input_stream_counter, relative_base


challenge = Challenge()
challenge.main()
