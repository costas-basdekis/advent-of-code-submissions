#!/usr/bin/env python3
import utils
from year_2017.day_08 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        6209
        """
        return InstructionSetExtended.from_instructions_text(_input)\
            .get_max_value_during_application()


class InstructionSetExtended(part_a.InstructionSet):
    def get_max_value_during_application(self, registers=None):
        """
        >>> instruction_set = InstructionSetExtended.from_instructions_text(
        ...     "b inc 5 if a > 1\\n"
        ...     "a inc 1 if b < 5\\n"
        ...     "c dec -10 if a >= 1\\n"
        ...     "c inc -20 if c == 10\\n"
        ... )
        >>> instruction_set.get_max_value_during_application()
        10
        >>> instruction_set.get_max_value_during_application({})
        10
        >>> instruction_set.get_max_value_during_application({'a': 5})
        10
        """
        _, max_value = self.apply_and_max_value(registers)
        return max_value

    def apply_and_max_value(self, registers=None):
        """
        >>> instruction_set = InstructionSetExtended.from_instructions_text(
        ...     "b inc 5 if a > 1\\n"
        ...     "a inc 1 if b < 5\\n"
        ...     "c dec -10 if a >= 1\\n"
        ...     "c inc -20 if c == 10\\n"
        ... )
        >>> instruction_set.apply_and_max_value()
        ({'a': 1, 'c': -10}, 10)
        >>> instruction_set.apply_and_max_value({})
        ({'a': 1, 'c': -10}, 10)
        >>> instruction_set.apply_and_max_value({'a': 5})
        ({'a': 5, 'b': 5, 'c': -10}, 10)
        """
        if registers is None:
            registers = {}
        max_value = max(registers.values(), default=0)
        for instruction in self.instructions:
            instruction.apply(registers)
            max_value = max(max_value, max(registers.values(), default=0))

        return registers, max_value


Challenge.main()
challenge = Challenge()
