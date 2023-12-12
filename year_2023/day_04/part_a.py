#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import Generic, List, Type, Union

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, TV


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        26346
        """
        return ScratchCardSet.from_cards_text(_input).get_total_points()


ScratchCardT = TV["ScratchCard"]


@dataclass
class ScratchCardSet(Generic[ScratchCardT]):
    cards: List[ScratchCardT]

    @classmethod
    def get_card_class(cls) -> Type[ScratchCardT]:
        return get_type_argument_class(cls, ScratchCardT)

    @classmethod
    def from_cards_text(cls, cards_text: str) -> "ScratchCardSet":
        """
        >>> ScratchCardSet.from_cards_text('''
        ...     Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
        ...     Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
        ...     Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
        ...     Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
        ...     Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
        ...     Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
        ... ''')
        ScratchCardSet(cards=[ScratchCard(id=1,
            winning_numbers=[41, 48, 83, 86, 17],
            numbers=[83, 86, 6, 31, 17, 9, 48, 53]), ...])
        """
        card_class = cls.get_card_class()
        return cls(
            list(map(card_class.from_card_text,
                     cards_text.strip().splitlines())),
        )

    def get_total_points(self) -> int:
        """
        >>> ScratchCardSet.from_cards_text('''
        ...     Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
        ...     Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
        ...     Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
        ...     Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
        ...     Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
        ...     Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
        ... ''').get_total_points()
        13
        """
        return sum((
            card.get_points()
            for card in self.cards
        ), 0)


@dataclass
class ScratchCard:
    id: int
    winning_numbers: List[int]
    numbers: List[int]

    re_text = re.compile(r"Card\s*(\d+): ([\d\s]+) \| ([\d\s]+)")

    @classmethod
    def from_card_text(cls, card_text: str) -> "ScratchCard":
        """
        >>> ScratchCard.from_card_text(
        ...     "     Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53")
        ScratchCard(id=1, winning_numbers=[41, 48, 83, 86, 17],
            numbers=[83, 86, 6, 31, 17, 9, 48, 53])
        """
        match = cls.re_text.match(card_text.strip())
        if not match:
            raise Exception(f"Could not parse '{card_text}'")
        id_str, winning_numbers_str, numbers_str = match.groups()
        return cls(
            int(id_str),
            list(map(int, filter(None, winning_numbers_str.split(" ")))),
            list(map(int, filter(None, numbers_str.split(" ")))),
        )

    def get_points(self) -> int:
        """
        >>> ScratchCard.from_card_text(
        ...     "Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53"
        ... ).get_points()
        8
        """
        count = len(self.get_winning_numbers())
        if not count:
            return 0
        return 2 ** (count - 1)

    def get_winning_numbers(self) -> List[int]:
        """
        >>> ScratchCard.from_card_text(
        ...     "Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53"
        ... ).get_winning_numbers()
        [17, 48, 83, 86]
        """
        return sorted(set(self.winning_numbers) & set(self.numbers))


Challenge.main()
challenge = Challenge()
