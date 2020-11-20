#!/usr/bin/env python3
import doctest
from abc import ABC

from utils import get_current_directory
from year_2019.day_05.part_b import get_program_result_and_output_extended
import year_2019.day_09.part_a


def solve(_input=None):
    """
    >>> solve()
    19348404
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    input_stream = get_script().as_input_stream()
    _, output = get_program_result_and_output_extended(_input, input_stream)
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

    def as_input_stream(self):
        """
        >>> "".join(map(chr, SpringScript().as_input_stream()))
        'WALK\\n'
        >>> "".join(map(chr, SpringScript().and_('T', 'J').as_input_stream()))
        'AND T J\\nWALK\\n'
        """
        return list(map(ord, self.as_input_text()))

    def as_input_text(self):
        """
        >>> SpringScript().as_input_text()
        'WALK\\n'
        >>> SpringScript().and_('T', 'J').as_input_text()
        'AND T J\\nWALK\\n'
        """
        return "".join(map("{}\n".format, self.instruction_lines)) + "WALK\n"

    PATH_PARSE_MAP = {
        ".": False,
        "#": True,
    }

    def simulate(self, path_text):
        """
        >>> SpringScript().simulate(".####.#..########")
        0
        >>> SpringScript().simulate("#####.#..########")
        5
        """
        path = tuple(map(self.PATH_PARSE_MAP.__getitem__, path_text))
        if not path:
            raise Exception("No path was passed")

        registers = {
            'T': False,
            'J': False,
            'A': None,
            'B': None,
            'C': None,
            'D': None,
        }
        position = 0
        while position < len(path):
            step = path[position]
            if not step:
                return position
            if position >= len(path) - 4:
                return None
            self.update_read_registers(
                path[position + 1:position + 5], registers)
            # print("before", registers)
            self.simulate_round(registers)
            if not registers['J']:
                advance = 1
            else:
                advance = 4
            position += advance

    def simulate_round(self, registers):
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
            line.simulate(registers)
            # print(line, registers)
        return registers

    def update_read_registers(self, path, registers):
        registers.update({
            'A': path[0],
            'B': path[1],
            'C': path[2],
            'D': path[3],
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
    READABLE_REGISTERS = WRITABLE_REGISTERS + ('A', 'B', 'C', 'D')

    operator = NotImplemented

    def check_writable(self, register):
        if register not in self.WRITABLE_REGISTERS:
            raise Exception(
                f"Register '{register}' is not a writable register")

    def check_readable(self, register):
        if register not in self.READABLE_REGISTERS:
            raise Exception(
                f"Register '{register}' is not a readable register")

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

    def simulate(self, registers):
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


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
