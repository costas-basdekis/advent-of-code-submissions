#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1766400
        """
        return part_a.IngredientSet.from_ingredients_text(_input)\
            .get_highest_score(exact_calories=500)


Challenge.main()
challenge = Challenge()
