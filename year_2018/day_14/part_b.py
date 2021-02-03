#!/usr/bin/env python3
import utils

from year_2018.day_14 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        20203532
        """
        return RecipeBoardExtended()\
            .tick_and_find_position(_input.strip(), debug=debug)


class RecipeBoardExtended(part_a.RecipeBoard):
    def tick_and_find_position(self, text, max_length=None, debug=False):
        """
        >>> RecipeBoardExtended().tick_and_find_position("51589", 9 + 5)
        9
        >>> RecipeBoardExtended().tick_and_find_position("01245", 5 + 5)
        5
        >>> RecipeBoardExtended().tick_and_find_position("92510", 18 + 5)
        18
        >>> RecipeBoardExtended().tick_and_find_position("59414", 2018 + 5)
        2018
        """
        sequence = self.sequence
        indexes = self.indexes
        while text not in sequence[-(len(text) + 2):]:
            if max_length is not None and max_length < len(sequence):
                raise Exception(f"Too big sequence, and couldn't find text")
            next_score = (
                int(sequence[indexes[0]])
                + int(sequence[indexes[1]])
            )
            sequence += str(next_score)
            indexes = (
                (
                    indexes[0]
                    + int(sequence[indexes[0]])
                    + 1
                ) % len(sequence),
                (
                    indexes[1]
                    + int(sequence[indexes[1]])
                    + 1
                ) % len(sequence),
            )
            if debug:
                if len(sequence) % 1000000 in (0, 1):
                    print(len(sequence))

        return sequence.index(text, len(sequence) - (len(text) + 2))


Challenge.main()
challenge = Challenge()
