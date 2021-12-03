#!/usr/bin/env python3
from typing import Any, Optional, List, Callable

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2015.day_22 import part_a
from year_2015.day_22.part_a import Game, CharacterEnum, Character


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> 1195 < Challenge().default_solve() < 1295
        True
        """
        return GameExtended\
            .from_boss_text(_input)\
            .find_min_mana_necessary(debugger)

    def play(self):
        GameExtended.from_boss_text(self.input).play()


class GameExtended(Game):
    def get_play_steps(
        self, character: Character, other: Character, option: Any,
    ) -> List[Callable[[], Optional[str]]]:
        steps = super().get_play_steps(character, other, option)
        if self.next_turn_character_type == CharacterEnum.Player:
            steps = [self.lose_1_hit_point] + steps

        return steps

    def lose_1_hit_point(self) -> Optional[str]:
        attack_amount = self.player.attack(1, force=True)
        assert attack_amount == 1
        return f"Player loses {attack_amount}HP"


Challenge.main()
challenge = Challenge()
