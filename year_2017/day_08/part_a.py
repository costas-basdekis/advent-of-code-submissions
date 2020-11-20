#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Callable, List

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        42
        """
        return InstructionSet.from_instructions_text(_input)\
            .get_max_value_after_application()


@dataclass
class InstructionSet:
    instructions: List['Instruction']

    @classmethod
    def from_instructions_text(cls, instructions_text):
        return cls(list(map(
            Instruction.from_instruction_text,
            instructions_text.strip().splitlines())))

    def get_max_value_after_application(self, registers=None):
        """
        >>> instruction_set = InstructionSet.from_instructions_text(
        ...     "b inc 5 if a > 1\\n"
        ...     "a inc 1 if b < 5\\n"
        ...     "c dec -10 if a >= 1\\n"
        ...     "c inc -20 if c == 10\\n"
        ... )
        >>> instruction_set.get_max_value_after_application()
        1
        >>> instruction_set.get_max_value_after_application({})
        1
        >>> instruction_set.get_max_value_after_application({'a': 5})
        5
        """
        registers = self.apply(registers)
        return max(registers.values(), default=0)

    def apply(self, registers=None):
        """
        >>> instruction_set = InstructionSet.from_instructions_text(
        ...     "b inc 5 if a > 1\\n"
        ...     "a inc 1 if b < 5\\n"
        ...     "c dec -10 if a >= 1\\n"
        ...     "c inc -20 if c == 10\\n"
        ... )
        >>> instruction_set.apply()
        {'a': 1, 'c': -10}
        >>> instruction_set.apply({})
        {'a': 1, 'c': -10}
        >>> instruction_set.apply({'a': 5})
        {'a': 5, 'b': 5, 'c': -10}
        """
        if registers is None:
            registers = {}
        for instruction in self.instructions:
            instruction.apply(registers)

        return registers


@dataclass
class Instruction:
    register: str
    offset: int
    condition: 'Condition'

    re_instruction = re.compile(r"^(\w+) (inc|dec) (-?\d+) if (.*)$")

    SIGN_BY_NAME = {
        'dec': -1,
        'inc': 1,
    }

    @classmethod
    def from_instruction_text(cls, instruction_text):
        """
        >>> Instruction.from_instruction_text('cde inc -20 if fgh == 10')
        Instruction(register='cde', offset=-20,
            condition=Condition(register='fgh',
                operation=<...__eq__...>, value=10))
        >>> Instruction.from_instruction_text('cde dec -20 if fgh == 10')
        Instruction(register='cde', offset=20,
            condition=Condition(register='fgh',
                operation=<...__eq__...>, value=10))
        >>> Instruction.from_instruction_text('cde dec 20 if fgh == 10')
        Instruction(register='cde', offset=-20,
            condition=Condition(register='fgh',
                operation=<...__eq__...>, value=10))
        """
        register, offset_sign_str, offset_str, condition_text = \
            cls.re_instruction.match(instruction_text).groups()
        offset_sign = cls.SIGN_BY_NAME[offset_sign_str]
        offset = offset_sign * int(offset_str)
        condition = Condition.from_condition_text(condition_text)

        return cls(register, offset, condition)

    def apply(self, registers):
        """
        >>> instruction = Instruction.from_instruction_text(
        ...     'cde inc -20 if fgh == 10')
        >>> instruction.apply({})
        {}
        >>> instruction.apply({'cde': 5})
        {'cde': 5}
        >>> instruction.apply({'cde': 5, 'fgh': 5})
        {'cde': 5, 'fgh': 5}
        >>> instruction.apply({'cde': 5, 'fgh': 10})
        {'cde': -15, 'fgh': 10}
        >>> instruction.apply({'cde': 5, 'fgh': 15})
        {'cde': 5, 'fgh': 15}
        >>> instruction.apply({'cde': 20, 'fgh': 10})
        {'fgh': 10}
        """
        if not self.condition.holds(registers):
            return registers
        register_value = registers.get(self.register, 0)
        new_value = register_value + self.offset
        if new_value == 0:
            if self.register in registers:
                del registers[self.register]
        else:
            registers[self.register] = new_value

        return registers



@dataclass
class Condition:
    register: str
    operation: Callable[[int, int], bool]
    value: int

    re_condition = re.compile(r"^(\w+) ([=!<>]+) (-?\d+)$")

    OPERATIONS_BY_NAME = {
        '==': int.__eq__,
        '!=': int.__ne__,
        '>=': int.__ge__,
        '<=': int.__le__,
        '>': int.__gt__,
        '<': int.__lt__,
    }

    @classmethod
    def from_condition_text(cls, condition_text):
        """
        >>> Condition.from_condition_text('fgh == 10')
        Condition(register='fgh', operation=<...__eq__...>, value=10)
        >>> Condition.from_condition_text('fgh == -10')
        Condition(register='fgh', operation=<...__eq__...>, value=-10)
        """
        match = cls.re_condition.match(condition_text)
        if not match:
            raise Exception(f"Could not parse Condition '{condition_text}'")
        register, operation_str, value_str = match.groups()
        operation = cls.OPERATIONS_BY_NAME[operation_str]
        value = int(value_str)

        return cls(register, operation, value)

    def holds(self, registers):
        """
        >>> Condition.from_condition_text('fgh == 10').holds({'abc': 10})
        False
        >>> Condition.from_condition_text('fgh == 10').holds({'fgh': 5})
        False
        >>> Condition.from_condition_text('fgh == 10').holds({'fgh': 10})
        True
        >>> Condition.from_condition_text('fgh == 10').holds({'fgh': 15})
        False
        """
        register_value = registers.get(self.register, 0)
        return self.holds_for_value(register_value)

    def holds_for_value(self, register_value):
        """
        >>> Condition.from_condition_text('fgh == 10').holds_for_value(5)
        False
        >>> Condition.from_condition_text('fgh == 10').holds_for_value(10)
        True
        >>> Condition.from_condition_text('fgh == 10').holds_for_value(15)
        False
        >>> Condition.from_condition_text('fgh >= 10').holds_for_value(5)
        False
        >>> Condition.from_condition_text('fgh >= 10').holds_for_value(10)
        True
        >>> Condition.from_condition_text('fgh >= 10').holds_for_value(15)
        True
        """
        return self.operation(register_value, self.value)


challenge = Challenge()
challenge.main()
