#!/usr/bin/env python3
from dataclasses import dataclass
import re
from enum import Enum
from functools import total_ordering
from typing import cast, Generic, List, Tuple, Type, Union

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, TV


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        246912307
        """
        return HandSet.from_hands_text(_input).get_winnings()


HandT = TV["Hand"]


@dataclass
class HandSet(Generic[HandT]):
    hands: List[HandT]

    @classmethod
    def get_hand_class(cls) -> Type[HandT]:
        return cast(Type[HandT], get_type_argument_class(cls, HandT))

    @classmethod
    def from_hands_text(cls, hands_text: str) -> "HandSet":
        """
        >>> HandSet.from_hands_text('''
        ...     32T3K 765
        ...     T55J5 684
        ...     KK677 28
        ...     KTJJT 220
        ...     QQQJA 483
        ... ''')
        HandSet(hands=[Hand(cards='32T3K', bid=765, type=HandType.OnePair),
            ...])
        """
        hand_class = cls.get_hand_class()
        return cls(hands=list(map(
            hand_class.from_hand_text,
            hands_text.strip().splitlines(),
        )))

    def get_winnings(self) -> int:
        """
        >>> HandSet.from_hands_text('''
        ...     32T3K 765
        ...     T55J5 684
        ...     KK677 28
        ...     KTJJT 220
        ...     QQQJA 483
        ... ''').get_winnings()
        6440
        """
        return sum((
            index * hand.bid
            for index, hand in enumerate(self.rank_hands(), 1)
        ), 0)

    def rank_hands(self) -> List[HandT]:
        """
        >>> [hand.cards for hand in HandSet.from_hands_text('''
        ...     32T3K 765
        ...     T55J5 684
        ...     KK677 28
        ...     KTJJT 220
        ...     QQQJA 483
        ... ''').rank_hands()]
        ['32T3K', 'KTJJT', 'KK677', 'T55J5', 'QQQJA']
        """
        return sorted(self.hands)


HandTypeT = TV["HandType"]


@dataclass
@total_ordering
class Hand(Generic[HandTypeT]):
    cards: str
    bid: int
    type: HandTypeT

    re_hand = re.compile(r"([AKQJT2-9]+)\s+(\d+)")
    rank_order = '23456789TJQKA'

    @classmethod
    def get_type_class(cls) -> Type[HandTypeT]:
        return cast(
            Type[HandTypeT],
            get_type_argument_class(cls, HandTypeT),
        )

    @classmethod
    def from_hand_text(cls, hand_text: str) -> "Hand":
        """
        >>> Hand.from_hand_text("32T3K 765")
        Hand(cards='32T3K', bid=765, type=HandType.OnePair)
        """
        cards_str, bid_str = cls.re_hand.match(hand_text.strip()).groups()
        type_class = cls.get_type_class()
        return cls(cards_str, int(bid_str), type_class.from_cards(cards_str))

    def __eq__(self, other) -> bool:
        """
        >>> Hand.from_hand_text("KK677 1") > Hand.from_hand_text("KTJJT 1")
        True
        """
        if not isinstance(other, Hand):
            raise NotImplementedError(
                f"Cannot compare instances of {type(self).__name__} "
                f"and {type(other).__name__}")
        return self.get_order_key() == other.get_order_key()

    def __lt__(self, other) -> bool:
        if not isinstance(other, Hand):
            raise NotImplementedError(
                f"Cannot compare instances of {type(self).__name__} "
                f"and {type(other).__name__}")
        return self.get_order_key() < other.get_order_key()

    def get_order_key(self) -> Tuple[HandTypeT, Tuple[int, ...]]:
        return self.type, tuple(map(self.rank_order.index, self.cards))


@total_ordering
class HandType(Enum):
    HighCard = 1
    OnePair = 2
    TwoPair = 3
    ThreeOfAKind = 4
    FullHouse = 5
    FourOfAKind = 6
    FiveOfAKind = 7

    @classmethod
    def from_cards(cls, cards: str) -> "HandType":
        """
        >>> HandType.from_cards("32T4K")
        HandType.HighCard
        >>> HandType.from_cards("32T3K")
        HandType.OnePair
        >>> HandType.from_cards("32T3T")
        HandType.TwoPair
        >>> HandType.from_cards("3233K")
        HandType.ThreeOfAKind
        >>> HandType.from_cards("3TT3T")
        HandType.FullHouse
        >>> HandType.from_cards("33T33")
        HandType.FourOfAKind
        >>> HandType.from_cards("33333")
        HandType.FiveOfAKind
        """
        cards_set = set(cards)
        first_rank_count = max(map(cards.count, cards_set))
        if len(cards_set) == 1:
            return cls.FiveOfAKind
        elif len(cards_set) == 2:
            if first_rank_count == 4:
                return cls.FourOfAKind
            elif first_rank_count == 3:
                return cls.FullHouse
        elif len(cards_set) == 3:
            if first_rank_count == 3:
                return cls.ThreeOfAKind
            elif first_rank_count == 2:
                return cls.TwoPair
        elif len(cards_set) == 4:
            return cls.OnePair
        else:
            return cls.HighCard
        raise Exception(
            f"Cannot interpret cards '{cards}' "
            f"(set: {cards_set}, first rank count: {first_rank_count})"
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, HandType):
            raise NotImplementedError(
                f"Cannot compare instances of {type(self).__name__} "
                f"and {type(other).__name__}")
        return self.value == other.value

    def __lt__(self, other) -> bool:
        if not isinstance(other, HandType):
            raise NotImplementedError(
                f"Cannot compare instances of {type(self).__name__} "
                f"and {type(other).__name__}")
        return self.value < other.value


Challenge.main()
challenge = Challenge()
