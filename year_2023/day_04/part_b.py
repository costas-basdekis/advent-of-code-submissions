#!/usr/bin/env python3
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_04.part_a import ScratchCardSet, ScratchCard


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        8467762
        """
        return ScratchCardSetExtended\
            .from_cards_text(_input)\
            .get_extended_points()


class ScratchCardSetExtended(ScratchCardSet[ScratchCard]):
    cards: List[ScratchCard]

    def get_extended_points(self) -> int:
        """
        >>> ScratchCardSetExtended.from_cards_text('''
        ...     Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
        ...     Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
        ...     Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
        ...     Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
        ...     Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
        ...     Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
        ... ''').get_extended_points()
        30
        """
        card_copy_counts = {
            card.id: 1
            for card in self.cards
        }
        for card in self.cards:
            win_count = len(card.get_winning_numbers())
            copy_count = card_copy_counts[card.id]
            for won_id in range(card.id + 1, card.id + win_count + 1):
                card_copy_counts[won_id] += copy_count

        return sum(card_copy_counts.values())


Challenge.main()
challenge = Challenge()
