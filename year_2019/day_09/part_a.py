#!/usr/bin/env python3
import utils

from year_2019.day_05.part_a import get_values
from year_2019.day_05.part_b import register_op_handler_extended, \
    get_program_result_and_output_extended


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        2738720997
        >>> get_program_result_and_output_extended(\
            '109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99', [])[1]
        [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]
        >>> get_program_result_and_output_extended(\
            '1102,34915192,34915192,7,4,7,99,0', [])[1]
        [1219070632396864]
        >>> get_program_result_and_output_extended(\
            '104,1125899906842624,99', [])[1]
        [1125899906842624]
        """
        _, output_stream = get_program_result_and_output_extended(_input, [1])

        *wrong_op_codes, boost_keycode = output_stream
        if wrong_op_codes:
            raise Exception("Some op codes were wrong")
        return boost_keycode


@register_op_handler_extended(9)
def handle_adjust_relative_base(parameter_modes, program, program_counter,
                                input_stream, input_stream_counter,
                                output_stream, relative_base):
    """
    >>> handle_adjust_relative_base('1', [9, 0, 99, 99], 0, [], 0, [], 0)
    (2, 0, 0)
    >>> handle_adjust_relative_base('1', [9, 1, 99, 99], 0, [], 0, [], 0)
    (2, 0, 1)
    >>> handle_adjust_relative_base('0', [9, 3, 99, 5, 99], 0, [], 0, [], 1)
    (2, 0, 6)
    >>> handle_adjust_relative_base('0', [9, 3, 99, -1, 99], 0, [], 0, [], 5)
    (2, 0, 4)
    >>> handle_adjust_relative_base('2', [9, -2, 99, -1, 99], 0, [], 0, [], 5)
    (2, 0, 4)
    """
    program_counter += 1
    _, (value_1,), program, program_counter = get_values(
        1, parameter_modes, program, program_counter, relative_base)

    relative_base += value_1

    return program_counter, input_stream_counter, relative_base


challenge = Challenge()
challenge.main()
