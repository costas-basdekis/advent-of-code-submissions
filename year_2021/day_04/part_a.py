#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from typing import List, Generic, Type, Set, Iterable, Tuple, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        2496
        """
        return BingoGame.from_game_text(_input).draw_until_finished()


NumberDrawerT = TV["NumberDrawer"]
BingoCardT = TV["BingoCard"]


@dataclass
class BingoGame(Generic[NumberDrawerT, BingoCardT]):
    drawer: NumberDrawerT
    cards: List[BingoCardT]

    @classmethod
    def get_drawer_class(cls) -> Type[NumberDrawerT]:
        return get_type_argument_class(cls, NumberDrawerT)

    @classmethod
    def get_card_class(cls) -> Type[BingoCardT]:
        return get_type_argument_class(cls, BingoCardT)

    @classmethod
    def from_game_text(cls, game_text: str) -> "BingoGame":
        """
        >>> BingoGame.from_game_text('''
        ... 7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1
        ...
        ... 22 13 17 11  0
        ...  8  2 23  4 24
        ... 21  9 14 16  7
        ...  6 10  3 18  5
        ...  1 12 20 15 19
        ...
        ...  3 15  0  2 22
        ...  9 18 13 17  5
        ... 19  8  7 25 23
        ... 20 11 10 24  4
        ... 14 21 16 12  6
        ...
        ... 14 21 17 24  4
        ... 10 16 15  9 19
        ... 18  8 23 26 20
        ... 22 11 13  6  5
        ...  2  0 12  3  7
        ... ''')
        BingoGame(drawer=NumberDrawer(numbers=[7, 4, 9, 5, 11, 17, 23, 2, 0,
            14, 21, 24, 10, 16, 13, 6, 15, 25, 12, 22, 18, 20, 8, 19, 3, 26,
            1], index=0), cards=[BingoCard(numbers=[[22, 13, 17, 11, 0],
                [8, 2, 23, 4, 24], [21, 9, 14, 16, 7], [6, 10, 3, 18, 5],
                [1, 12, 20, 15, 19]], found=set()), ...])
        """
        blocks = game_text.strip().split("\n\n")
        drawer_block, *card_blocks = blocks
        drawer_class = cls.get_drawer_class()
        card_class = cls.get_card_class()
        return cls(
            drawer=drawer_class.from_drawer_text(drawer_block),
            cards=list(map(card_class.from_card_text, card_blocks))
        )

    def draw(self) -> "BingoGame":
        number = self.drawer.draw()
        for card in self.cards:
            card.mark(number)

        return self

    def draw_many(self, count: int) -> "BingoGame":
        """
        >>> game = BingoGame.from_game_text('''
        ... 7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1
        ...
        ... 22 13 17 11  0
        ...  8  2 23  4 24
        ... 21  9 14 16  7
        ...  6 10  3 18  5
        ...  1 12 20 15 19
        ...
        ...  3 15  0  2 22
        ...  9 18 13 17  5
        ... 19  8  7 25 23
        ... 20 11 10 24  4
        ... 14 21 16 12  6
        ...
        ... 14 21 17 24  4
        ... 10 16 15  9 19
        ... 18  8 23 26 20
        ... 22 11 13  6  5
        ...  2  0 12  3  7
        ... ''')
        >>> game.has_finished
        False
        >>> game.draw_many(11).has_finished
        False
        >>> game.draw_many(1).has_won
        True
        >>> print(game.cards[2])
        14.21.17.24. 4.
        10 16 15  9.19
        18  8 23.26 20
        22 11.13  6  5.
         2. 0.12  3  7.
        >>> game.winning_score
        4512
        """
        for _ in range(count):
            self.draw()

        return self

    def draw_until_finished(self) -> Optional[int]:
        while not self.has_finished:
            self.draw()

        if not self.has_won:
            return None
        return self.winning_score

    @property
    def has_finished(self) -> bool:
        return (
            self.drawer.has_finished
            or self.has_won
        )

    @property
    def has_won(self):
        return any(card.has_won for card in self.cards)

    @property
    def winning_score(self) -> int:
        winning_cards = self.winning_cards
        if not winning_cards:
            raise Exception("No card has won yet")
        if len(winning_cards) > 1:
            raise Exception(f"Multiple cards ({len(winning_cards)}) have won")
        winning_card, = winning_cards
        return winning_card.get_winning_score(self.drawer.current_number)

    @property
    def winning_cards(self) -> List[BingoCardT]:
        return [
            card
            for card in self.cards
            if card.has_won
        ]


@dataclass
class NumberDrawer:
    numbers: List[int]
    index: int = 0

    @classmethod
    def from_drawer_text(cls, drawer_test: str) -> "NumberDrawer":
        """
        >>> NumberDrawer.from_drawer_text(
        ...     "7,4,9,5,11,17,23,2,0,14,21,24,10,16"
        ...     ",13,6,15,25,12,22,18,20,8,19,3,26,1"
        ... )
        NumberDrawer(numbers=[7, 4, 9, 5, 11, 17, 23, 2, 0, 14, 21, 24, 10, 16,
            13, 6, 15, 25, 12, 22, 18, 20, 8, 19, 3, 26, 1], index=0)
        """
        return cls(numbers=list(map(int, drawer_test.split(","))))

    @property
    def current_number(self) -> int:
        if self.index < 0:
            raise Exception("There is no current number")
        if self.index - 1 >= len(self.numbers):
            raise Exception(
                f"Index {self.index - 1} is beyond numbers of length "
                f"{len(self.numbers)}"
            )
        return self.numbers[self.index - 1]

    @property
    def next_number(self) -> int:
        if self.has_finished:
            raise Exception(
                f"Index {self.index} is beyond numbers of length "
                f"{len(self.numbers)}"
            )
        return self.numbers[self.index]

    def draw(self) -> int:
        """
        >>> drawer = NumberDrawer(numbers=[7, 4, 9, 5, 11, 17, 23, 2, 0, 14,
        ...     21, 24, 10, 16, 13, 6, 15, 25, 12, 22, 18, 20, 8, 19, 3, 26,
        ...     1], index=0)
        >>> drawer.draw()
        7
        >>> drawer
        NumberDrawer(numbers=[7, 4, 9, 5, 11, 17, 23, 2, 0, 14, 21, 24, 10, 16,
            13, 6, 15, 25, 12, 22, 18, 20, 8, 19, 3, 26, 1], index=1)
        >>> NumberDrawer(numbers=[7, 4, 9, 5, 11, 17, 23, 2, 0, 14, 21, 24, 10,
        ...     16, 13, 6, 15, 25, 12, 22, 18, 20, 8, 19, 3, 26,
        ...     1], index=27).draw()
        Traceback (most recent call last):
        ...
        Exception: Index 27 is beyond numbers of length 27
        """
        number = self.next_number
        self.index += 1
        return number

    @property
    def has_finished(self) -> bool:
        return self.index >= len(self.numbers)


@dataclass
class BingoCard:
    numbers: List[List[int]]
    found: Set[int] = field(default_factory=set)

    @classmethod
    def from_card_text(cls, card_text: str) -> "BingoCard":
        """
        >>> BingoCard.from_card_text('''
        ...     22 13 17 11  0
        ...      8  2 23  4 24
        ...     21  9 14 16  7
        ...      6 10  3 18  5
        ...      1 12 20 15 19
        ... ''')
        BingoCard(numbers=[[22, 13, 17, 11, 0], [8, 2, 23, 4, 24],
            [21, 9, 14, 16, 7], [6, 10, 3, 18, 5], [1, 12, 20, 15, 19]],
            found=set())
        """
        lines = card_text.strip().splitlines()
        return cls(numbers=[
            list(map(int, filter(None, line.split(" "))))
            for line in lines
        ])

    @classmethod
    def from_text(cls, text: str) -> "BingoCard":
        """
        >>> print(BingoCard.from_text('''
        ...     22 13 17 11. 0
        ...      8  2 23  4 24
        ...     21  9 14 16  7
        ...      6 10  3 18  5.
        ...      1 12 20 15 19
        ... '''))
        22 13 17 11. 0
         8  2 23  4 24
        21  9 14 16  7
         6 10  3 18  5.
         1 12 20 15 19
        """
        numbers_and_found = list(map(
            cls.match_text_line,
            filter(None, map(str.strip, text.splitlines()))
        ))
        return cls(
            numbers=[
                [
                    number
                    for number, _ in line
                ]
                for line in numbers_and_found
            ],
            found={
                number
                for line in numbers_and_found
                for number, number_found in line
                if number_found
            },
        )

    re_text_line = re.compile(
        r"^\s*"
        r"([ \d]?\d[ .])"
        r"([ \d]\d[ .])"
        r"([ \d]\d[ .])"
        r"([ \d]\d[ .])"
        r"([ \d]\d[ .]?)"
        r"\s*$"
    )

    re_text_line_group = re.compile(r"^([ \d]?\d)([ .]?)$")

    @classmethod
    def match_text_line(cls, line: str) -> List[Tuple[int, bool]]:
        match = cls.re_text_line.match(line.strip())
        if not match:
            raise Exception(f"Could not parse line '{line}'")
        return [
            (int(number_str), found_str == ".")
            for group in match.groups()
            for number_str, found_str
            in [cls.re_text_line_group.match(group).groups()]
        ]

    def __str__(self):
        """
        >>> print(BingoCard(numbers=[[22, 13, 17, 11, 0],
        ...     [8, 2, 23, 4, 24], [21, 9, 14, 16, 7], [6, 10, 3, 18, 5],
        ...     [1, 12, 20, 15, 19]]))
        22 13 17 11  0
         8  2 23  4 24
        21  9 14 16  7
         6 10  3 18  5
         1 12 20 15 19
        >>> print(BingoCard(numbers=[[22, 13, 17, 11, 0],
        ...     [8, 2, 23, 4, 24], [21, 9, 14, 16, 7], [6, 10, 3, 18, 5],
        ...     [1, 12, 20, 15, 19]]).mark(88))
        22 13 17 11  0
         8  2 23  4 24
        21  9 14 16  7
         6 10  3 18  5
         1 12 20 15 19
        >>> print(BingoCard(numbers=[[22, 13, 17, 11, 0],
        ...     [8, 2, 23, 4, 24], [21, 9, 14, 16, 7], [6, 10, 3, 18, 5],
        ...     [1, 12, 20, 15, 19]]).mark(11))
        22 13 17 11. 0
         8  2 23  4 24
        21  9 14 16  7
         6 10  3 18  5
         1 12 20 15 19
        >>> print(BingoCard(numbers=[[22, 13, 17, 11, 0],
        ...     [8, 2, 23, 4, 24], [21, 9, 14, 16, 7], [6, 10, 3, 18, 5],
        ...     [1, 12, 20, 15, 19]]).mark(11).mark(5))
        22 13 17 11. 0
         8  2 23  4 24
        21  9 14 16  7
         6 10  3 18  5.
         1 12 20 15 19
        """
        return "\n".join(
            "".join(
                f"{number: >2d}{found_separator}"
                for number in line
                for found in [number in self.found]
                for found_separator in ["." if found else " "]
            ).rstrip()
            for line in self.numbers
        )

    def __hash__(self):
        return hash(id(self))

    @property
    def all_numbers(self) -> Set[int]:
        return set(sum(self.numbers, []))

    def mark(self, number: int) -> "BingoCard":
        if number not in self.found and number in self.all_numbers:
            self.found.add(number)

        return self

    @property
    def has_won(self) -> bool:
        """
        >>> BingoCard.from_text('''
        ...     22 13 17 11. 0
        ...      8  2 23  4 24
        ...     21  9 14 16  7
        ...      6 10  3 18  5.
        ...      1 12 20 15 19
        ... ''').has_won
        False
        >>> BingoCard.from_text('''
        ...     22.13 17 11. 0
        ...      8  2.23  4 24
        ...     21  9 14.16  7
        ...      6 10  3 18. 5.
        ...      1 12 20 15 19.
        ... ''').has_won
        False
        >>> BingoCard.from_text('''
        ...     22.13.17.11. 0.
        ...      8  2 23  4 24
        ...     21  9 14 16  7
        ...      6 10  3 18  5.
        ...      1 12 20 15 19
        ... ''').has_won
        True
        >>> BingoCard.from_text('''
        ...     22.13 17 11. 0
        ...      8. 2 23  4 24
        ...     21. 9 14 16  7
        ...      6.10  3 18  5.
        ...      1.12 20 15 19
        ... ''').has_won
        True
        """
        return (
            any(map(self.are_numbers_found, self.numbers))
            or any(map(self.are_numbers_found, zip(*self.numbers)))
        )

    def are_numbers_found(self, numbers: Iterable[int]) -> bool:
        return all(number in self.found for number in numbers)

    def get_winning_score(self, last_called_number: int) -> int:
        """
        >>> BingoCard.from_text('''
        ...     14.21.17.24. 4.
        ...     10 16 15  9.19
        ...     18  8 23.26 20
        ...     22 11.13  6  5.
        ...      2. 0.12  3  7.
        ... ''').get_winning_score(24)
        4512
        """
        if not self.has_won:
            raise Exception("Board hasn't won")
        return sum(
            number
            for line in self.numbers
            for number in line
            if number not in self.found
        ) * last_called_number


Challenge.main()
challenge = Challenge()
