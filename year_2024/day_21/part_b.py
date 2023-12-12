#!/usr/bin/env python3
import string
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_21 import part_a

PairwiseCache = Dict[Tuple[str, str], List[str]]
KeychainPairwiseCache = Dict[int, PairwiseCache]
PairwiseLengthCache = Dict[Tuple[str, str], int]
LevelPairwiseLengthCache = Dict[int, PairwiseLengthCache]


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        279638326609472
        """
        return OptimisedKeypadChain.get_codes_min_total_complexity_from_text(_input, small_count=25)

    def play(self):
        print(OptimisedKeypadChain.default(25).get_keypress_min_length("029A"))


@dataclass
class OptimisedKeypadChain(part_a.KeypadChain):
    keypads: List[part_a.Keypad] = field(default_factory=list)

    def get_code_complexity(self, buttons: str, keypresses: Optional[str] = None) -> int:
        if keypresses is not None:
            return super().get_code_complexity(buttons, keypresses=keypresses)
        return self.get_code_complexity_via_length(buttons)

    def get_code_complexity_via_length(self, buttons: str, length: Optional[int] = None) -> int:
        """
        >>> OptimisedKeypadChain.default(2).get_code_complexity("029A")
        1972
        """
        if length is None:
            length = self.get_keypress_min_length(buttons)
        numeric_part = int("".join(char for char in buttons if char in string.digits))
        return length * numeric_part

    def get_keypress_min_length(self, buttons: str) -> int:
        """
        >>> OptimisedKeypadChain.default(2).get_keypress_min_length("029A")
        68
        """
        level_pairwise_length_cache: LevelPairwiseLengthCache = {level: {} for level in range(len(self.keypads))}
        return sum(
            self.get_point_keypress_min_length(source_button, target_button, level_pairwise_length_cache=level_pairwise_length_cache)
            for source_button, target_button in zip("A" + buttons, buttons)
        )

    def get_point_keypress_min_length(self, source_button: str, target_button: str, level_pairwise_length_cache: Optional[LevelPairwiseLengthCache] = None) -> int:
        """
        >>> OptimisedKeypadChain().get_point_keypress_min_length("3", "0")
        1
        >>> OptimisedKeypadChain.default(0).get_point_keypress_min_length("3", "0")
        3
        """
        if level_pairwise_length_cache is None:
            level_pairwise_length_cache: LevelPairwiseLengthCache = {level: {} for level in range(len(self.keypads))}
        return self.get_point_keypress_min_length_at_level(source_button, target_button, 0, level_pairwise_length_cache)

    def get_point_keypress_min_length_at_level(self, source_button: str, target_button: str, level: int, level_pairwise_length_cache: LevelPairwiseLengthCache) -> int:
        if level == len(self.keypads):
            return 1
        pairwise_length_cache = level_pairwise_length_cache[level]
        if (source_button, target_button) in pairwise_length_cache:
            return pairwise_length_cache[(source_button, target_button)]
        keypad = self.keypads[level]
        next_keypresses = keypad.get_possible_point_keypresses(source_button, target_button)
        min_length = min(
            sum(
                self.get_point_keypress_min_length_at_level(next_source_button, next_target_button, level + 1, level_pairwise_length_cache)
                for next_source_button, next_target_button in zip("A" + next_keypress, next_keypress)
            )
            for next_keypress in next_keypresses
        )
        pairwise_length_cache[(source_button, target_button)] = min_length
        return min_length


Challenge.main()
challenge = Challenge()
