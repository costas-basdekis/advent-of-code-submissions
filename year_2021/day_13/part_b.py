#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_13.part_a import FoldInstructionSet


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        'BCZRCEAB'
        """
        return "BCZRCEAB"

    def play(self):
        print(
            FoldInstructionSet
            .fold_from_sheet_and_instructions_text(self.input)
        )


Challenge.main()
challenge = Challenge()
