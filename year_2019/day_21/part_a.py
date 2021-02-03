#!/usr/bin/env python3
from abc import ABC

import utils

from year_2019.day_05.part_b import get_program_result_and_output_extended
import year_2019.day_09.part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        19348404
        """
        return run_spring_robot(get_script(), _input)


def run_spring_robot(script, program_text, running=False):
    input_stream = script.as_input_stream(running=running)
    _, output = get_program_result_and_output_extended(
        program_text, input_stream)
    if not output:
        raise Exception("No output")
    if output[-1] <= 255:
        print("".join(map(chr, output)))
        return None

    solution = output[-1]
    return solution


def get_script():
    """
    >>> script = get_script()
    >>> script.simulate("#####.#..########")
    >>> script.simulate("#####...#########")
    """

    return SpringScript()\
        .not_('A', 'J')\
        .not_('C', 'T')\
        .or_('T', 'J')\
        .and_('D', 'J')


class SpringScript:
    def __init__(self, instruction_lines=()):
        self.instruction_lines = ()
        self.add_instruction_lines(instruction_lines)

    def as_input_stream(self, running=False):
        """
        >>> "".join(map(chr, SpringScript().as_input_stream()))
        'WALK\\n'
        >>> "".join(map(chr, SpringScript().and_('T', 'J').as_input_stream()))
        'AND T J\\nWALK\\n'
        >>> "".join(map(chr, SpringScript().as_input_stream(True)))
        'RUN\\n'
        >>> "".join(map(chr, SpringScript().and_('T', 'J').as_input_stream(True)))
        'AND T J\\nRUN\\n'
        """
        return list(map(ord, self.as_input_text(running=running)))

    def as_input_text(self, running=False):
        """
        >>> SpringScript().as_input_text()
        'WALK\\n'
        >>> SpringScript().and_('T', 'J').as_input_text()
        'AND T J\\nWALK\\n'
        >>> SpringScript().as_input_text(True)
        'RUN\\n'
        >>> SpringScript().and_('T', 'J').as_input_text(True)
        'AND T J\\nRUN\\n'
        """
        return "".join(map("{}\n".format, self.instruction_lines)) + (
            "RUN\n"
            if running else
            "WALK\n"
        )

    PATH_PARSE_MAP = {
        ".": False,
        "#": True,
    }

    def simulate(self, path_text, running=False):
        """
        >>> SpringScript().simulate(".####.#..###########")
        0
        >>> SpringScript().simulate("#####.#..###########")
        5
        """
        path = tuple(map(self.PATH_PARSE_MAP.__getitem__, path_text))
        if not path:
            raise Exception("No path was passed")

        registers = {
            'T': False,
            'J': False,
            **{
                register: None
                for register in SSOperator.RUN_GROUND_REGISTERS
            },
        }
        position = 0
        reading_count = len(SSOperator.RUN_GROUND_REGISTERS)
        while position < len(path):
            step = path[position]
            if not step:
                return position
            if position >= len(path) - reading_count:
                return None
            self.update_read_registers(
                path[position + 1:position + 1 + reading_count], registers,
                running=running)
            # print("before", registers)
            self.simulate_round(registers, running=running)
            if not registers['J']:
                advance = 1
            else:
                advance = 4
            position += advance

    def simulate_round(self, registers, running=False):
        """
        >>> SpringScript().set_('D', 'J').not_('A', 'T').or_('T', 'J')\\
        ...     .simulate_round({
        ...         'T': False, 'J': True,
        ...         'A': False, 'B': True, 'C': False, 'D': False,
        ...     })
        {'T': True, 'J': True, 'A': False, 'B': True, 'C': False, 'D': False}
        >>> SpringScript().set_('D', 'J').not_('A', 'T').or_('T', 'J')\\
        ...     .simulate_round({
        ...         'T': False, 'J': True,
        ...         'A': False, 'B': True, 'C': False, 'D': False,
        ...     })
        {'T': True, 'J': True, 'A': False, 'B': True, 'C': False, 'D': False}
        """
        for line in self.instruction_lines:
            line.simulate(registers, running=running)
            # print(line, registers)
        return registers

    def update_read_registers(self, path, registers, running=False):
        if running:
            ground_registers = SSOperator.RUN_GROUND_REGISTERS
        else:
            ground_registers = SSOperator.WALK_GROUND_REGISTERS
        registers.update({
            register: reading
            for register, reading in zip(ground_registers, path)
        })

    def add_instruction_lines(self, lines):
        lines = tuple(lines)
        new_lines = self.instruction_lines + lines
        if len(new_lines) > 20:
            raise Exception(
                f"Too many instruction lines: {len(new_lines)} > {20}")

        self.instruction_lines = new_lines

    def add_instruction_line(self, line):
        return self.add_instruction_lines((line,))

    def not_(self, a, b):
        self.add_instruction_line(SSNot(a, b))
        return self

    def and_(self, a, b):
        self.add_instruction_line(SSAnd(a, b))
        return self

    def or_(self, a, b):
        self.add_instruction_line(SSOr(a, b))
        return self

    def false_(self, a):
        return self\
            .not_('T', a)\
            .and_('T', a)

    def true_(self, a):
        return self\
            .not_('T', a)\
            .or_('T', a)

    def set_(self, a, b):
        return self\
            .or_(a, b)\
            .and_(a, b)


class SSOperator:
    WRITABLE_REGISTERS = ('T', 'J')
    WALK_GROUND_REGISTERS = ('A', 'B', 'C', 'D')
    RUN_ONLY_GROUND_REGISTERS = ('E', 'F', 'G', 'H', 'I')
    RUN_GROUND_REGISTERS = WALK_GROUND_REGISTERS + RUN_ONLY_GROUND_REGISTERS
    WALK_REGISTERS = WRITABLE_REGISTERS + WALK_GROUND_REGISTERS
    READABLE_REGISTERS = WRITABLE_REGISTERS + RUN_GROUND_REGISTERS

    operator = NotImplemented

    def check_writable(self, register):
        if register not in self.WRITABLE_REGISTERS:
            raise Exception(
                f"Register '{register}' is not a writable register")

    def check_readable(self, register):
        if register not in self.READABLE_REGISTERS:
            raise Exception(
                f"Register '{register}' is not a readable register")

    def check_walking(self, register):
        if register not in self.WALK_REGISTERS:
            raise Exception(
                f"Register '{register}' is not a walking register")

    def simulate(self, registers):
        raise NotImplementedError()


class SSBinary(SSOperator, ABC):
    binary_operation = NotImplemented

    def __init__(self, a, b):
        self.check_readable(a)
        self.check_writable(b)
        self.a, self.b = a, b

    def __str__(self):
        return f"{self.operator} {self.a} {self.b}"

    def simulate(self, registers, running=False):
        if not running:
            self.check_walking(self.a)
            self.check_walking(self.b)
        registers[self.b] = self.binary_operation(
            registers[self.a], registers[self.b])
        return registers


class SSOr(SSBinary):
    operator = 'OR'
    binary_operation = staticmethod(bool.__or__)


class SSAnd(SSBinary):
    operator = 'AND'
    binary_operation = staticmethod(bool.__and__)


class SSNot(SSBinary):
    """
    >>> SSNot('A', 'T').simulate({'A': False, 'T': False})
    {'A': False, 'T': True}
    """
    operator = 'NOT'

    def binary_operation(self, a, b):
        return not a


Challenge.main()
challenge = Challenge()
