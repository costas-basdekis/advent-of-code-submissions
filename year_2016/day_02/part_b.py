#!/usr/bin/env python3
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'C1A88'
        """
        instruction_lines = part_a.InstructionLine.from_lines_text(_input)
        return part_a.Numpad.standard_13_buttons().get_code(instruction_lines)


Challenge.main()
challenge = Challenge()
