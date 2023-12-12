#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, Cls, Self,
)
from year_2023.day_07.part_a import HandType, Hand, HandSet


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        246894760
        """
        hand_set = HandSetExtended.from_hands_text(_input)
        if debugger:
            for rank, hand in enumerate(hand_set.rank_hands(), 1):
                if "J" not in hand.cards:
                    continue
                debugger.report(f"{rank}: {''.join(sorted(hand.cards))} ({hand.cards}) {hand.type.name}")
        return hand_set.get_winnings()


class HandSetExtended(HandSet["HandExtended"]):
    """
    >>> hand_set = HandSetExtended.from_hands_text('''
    ...     32T3K 765
    ...     T55J5 684
    ...     KK677 28
    ...     KTJJT 220
    ...     QQQJA 483
    ... ''')
    >>> [hand.cards for hand in hand_set.rank_hands()]
    ['32T3K', 'KK677', 'T55J5', 'QQQJA', 'KTJJT']
    >>> hand_set.get_winnings()
    5905
    """


class HandExtended(Hand["HandTypeExtended"]):
    rank_order = 'J23456789TQKA'


class HandTypeExtended:
    @classmethod
    def from_cards(cls, cards: str) -> "HandType":
        """
        >>> HandTypeExtended.from_cards("T55J5")
        HandType.FourOfAKind
        >>> HandTypeExtended.from_cards("AAAAJ")
        HandType.FiveOfAKind
        """
        if "J" in cards:
            return max(
                HandType.from_cards(cards.replace("J", rank))
                for rank in "23456789TQKA"
            )
        return HandType.from_cards(cards)


Challenge.main()
challenge = Challenge()
