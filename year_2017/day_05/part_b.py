#!/usr/bin/env python3
import utils
from year_2017.day_05 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        26395586
        """
        return MessageExtended.from_text(_input).step_many().steps


class MessageExtended(part_a.Message):
    """
    >>> MessageExtended.from_text("0\\n3\\n0\\n1\\n-3").step_many()
    MessageExtended(instructions=[2, 3, 2, 3, -1], position=..., steps=10)
    """
    def update_instruction(self):
        if self.instructions[self.position] < 3:
            self.instructions[self.position] += 1
        else:
            self.instructions[self.position] -= 1


challenge = Challenge()
challenge.main()
