#!/usr/bin/env python3
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        4042
        """
        bot_set = part_a.InstructionSet\
            .get_bot_set_from_instructions_text(_input)
        bot_set.resolve()
        return (
            bot_set.outputs[0]
            * bot_set.outputs[1]
            * bot_set.outputs[2]
        )


Challenge.main()
challenge = Challenge()
