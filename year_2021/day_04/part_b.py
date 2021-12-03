#!/usr/bin/env python3
from typing import Optional

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_04 import part_a
from year_2021.day_04.part_a import BingoGame


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        25925
        """
        return BingoGameExtended\
            .from_game_text(_input)\
            .draw_until_all_cards_won()


class BingoGameExtended(BingoGame):
    def draw_until_all_cards_won(self) -> Optional[int]:
        previous_winning_cards = set()
        winning_cards = set()
        while not self.have_all_cards_won and not self.drawer.has_finished:
            self.draw()
            previous_winning_cards = winning_cards
            winning_cards = set(self.winning_cards)

        if not self.have_all_cards_won:
            return None

        new_winning_cards = winning_cards - previous_winning_cards
        if not new_winning_cards:
            raise Exception("Expected at least one new winning card")
        if len(new_winning_cards) > 1:
            raise Exception(
                f"Too many ({len(new_winning_cards)}) new winning cards"
            )
        new_winning_card, = new_winning_cards
        return new_winning_card.get_winning_score(self.drawer.current_number)

    @property
    def have_all_cards_won(self):
        return set(self.winning_cards) == set(self.cards)


Challenge.main()
challenge = Challenge()
