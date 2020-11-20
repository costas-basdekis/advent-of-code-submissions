#!/usr/bin/env python3
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'ZFHFSFOGPO'
        """
        result = part_a.InstructionSet.result_from_instructions_text(_input)
        if debug:
            print(result.show())

        return 'ZFHFSFOGPO'


Challenge.main()
challenge = Challenge()
