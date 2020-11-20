#!/usr/bin/env python3
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        9227647
        """
        return part_a.InstructionSet.from_instructions_text(_input)\
            .apply(part_a.State({'c': 1}), debug=debug)['a']


Challenge.main()
challenge = Challenge()
