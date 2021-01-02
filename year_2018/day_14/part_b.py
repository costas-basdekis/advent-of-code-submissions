#!/usr/bin/env python3
import utils

from year_2018.day_14 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        42
        """

        return RecipeBoardExtended().tick_and_find_position(_input)


class RecipeBoardExtended(part_a.RecipeBoard):
    def tick_and_find_position(self, text, max_length=None):
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
        result = self
        position = self.get_position(text)
        if position is not None:
            return position
        suffix_length = len(text) + 2
        while text not in result.get_suffix_string(suffix_length):
            if max_length is not None and max_length < len(result.sequence):
                raise Exception(
                    f"Too big sequence, and couldn't find text: naive answer "
                    f"is {result.get_position(text)}")
            result = result.tick()
            print(len(result.sequence), result.get_suffix_string(suffix_length))
        suffix = result.get_suffix_string(suffix_length)
        suffix_index = suffix.index(text)
        index = len(result.sequence) - suffix_length + suffix_index

        return index

    def get_position(self, text):
        """
        >>> RecipeBoardExtended().tick_many(15).get_position("51589")
        9
        >>> RecipeBoardExtended().tick_many(15).get_position("01245")
        5
        >>> RecipeBoardExtended().tick_many(23).get_position("92510")
        18
        >>> RecipeBoardExtended().tick_many(2023).get_position("59414")
        2018
        """
        try:
            return self.get_suffix_string().index(text)
        except ValueError:
            return None

    def get_suffix_string(self, length=None):
        if length is None:
            suffix = self.sequence
        else:
            suffix = self.sequence[-length:]
        return "".join(map(str, suffix))


challenge = Challenge()
challenge.main()
