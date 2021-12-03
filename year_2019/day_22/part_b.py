#!/usr/bin/env python3
import math
from dataclasses import dataclass
from functools import reduce
from operator import add
from typing import Union, Callable, Tuple

from abc import ABC

import utils
from aox.challenge import Debugger
from year_2019.day_22 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """"""
        """
        >>> Challenge().default_solve()
        56894170832118
        """
        return self.default_solve_for(
            index=2020,
            size=119315717514047,
            count=101741582076661,
            debugger=debugger,
        )

    def default_solve_for(
        self, index, size, count, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> Challenge().default_solve_for(index=2496, size=10007, count=1)
        2019
        """
        return ShufflesExtended.parse(self.input)\
            .to_modulo_shuffle_for_size(size)\
            .get_index_at_position_after_shuffle_many(
                index=index,
                count=count,
                debugger=debugger,
            )


class ShufflesExtended(part_a.Shuffles):
    def __init__(self, shuffles):
        super().__init__(shuffles)
        self.reverse_shuffles = list(reversed(self.shuffles))

    def to_modulo_shuffle_for_size(self, size: int) -> "ModuloShuffle":
        if not self.shuffles:
            raise Exception(f"Cannot convert empty shuffle list to modulo")

        return reduce(add, (
            shuffle.to_modulo_shuffle_for_size(size)
            for shuffle in self.shuffles
        ))

    def shuffle_deck_many(self, deck, count):
        """
        >>> part_a_shuffle = part_a.Shuffles.parse(
        ...     "deal into new stack\\n"
        ...     "cut -2\\n"
        ...     "deal with increment 7\\n"
        ...     "cut 8\\n"
        ...     "cut -4\\n"
        ...     "deal with increment 7\\n"
        ...     "cut 3\\n"
        ...     "deal with increment 9\\n"
        ...     "deal with increment 3\\n"
        ...     "cut -1\\n"
        ... )
        >>> part_b_shuffle = ShufflesExtended.parse(
        ...     "deal into new stack\\n"
        ...     "cut -2\\n"
        ...     "deal with increment 7\\n"
        ...     "cut 8\\n"
        ...     "cut -4\\n"
        ...     "deal with increment 7\\n"
        ...     "cut 3\\n"
        ...     "deal with increment 9\\n"
        ...     "deal with increment 3\\n"
        ...     "cut -1\\n"
        ... )
        >>> part_a_shuffle.shuffle_deck_many(tuple(range(10)), 31) \\
        ...     == part_b_shuffle.shuffle_deck_many(tuple(range(10)), 31)
        True
        """
        return tuple(
            self.get_card_at_position_after_shuffle_many(deck, count, index)
            for index in range(len(deck))
        )

    def shuffle_deck(self, deck):
        """
        >>> ShufflesExtended.parse(
        ...     "deal into new stack\\n"
        ...     "cut -2\\n"
        ...     "deal with increment 7\\n"
        ...     "cut 8\\n"
        ...     "cut -4\\n"
        ...     "deal with increment 7\\n"
        ...     "cut 3\\n"
        ...     "deal with increment 9\\n"
        ...     "deal with increment 3\\n"
        ...     "cut -1\\n"
        ... ).shuffle_deck(tuple(range(10)))
        (9, 2, 5, 8, 1, 4, 7, 0, 3, 6)
        """
        return tuple(
            self.get_card_at_position_after_shuffle_many(deck, 1, index)
            for index in range(len(deck))
        )

    def get_card_at_position_after_shuffle_many(
        self, deck, count, index, debugger: Debugger = Debugger(enabled=False),
    ):
        index = self.get_index_for_position_after_many_shuffles(
            index, count, len(deck), debugger=debugger)
        return deck[index]

    def get_index_for_position_after_many_shuffles(
        self, index, count, size, debugger: Debugger = Debugger(enabled=False),
    ):
        cycle = list(self.get_index_cycle(
            index, size, max_count=count, debugger=debugger))
        return cycle[(count - 1) % len(cycle)]

    def get_index_cycle(
        self, index, size, max_count=None,
        debugger: Debugger = Debugger(enabled=False),
    ):
        """
        >>> list(ShufflesExtended.parse(
        ...         "deal into new stack\\n"
        ...         "cut -2\\n"
        ...         "deal with increment 7\\n"
        ...         "cut 8\\n"
        ...         "cut -4\\n"
        ...         "deal with increment 7\\n"
        ...         "cut 3\\n"
        ...         "deal with increment 9\\n"
        ...         "deal with increment 3\\n"
        ...         "cut -1\\n"
        ... ).get_index_cycle(0, 10))
        [9, 6, 7, 0]
        >>> list(ShufflesExtended.parse(
        ...         "deal into new stack\\n"
        ...         "cut -2\\n"
        ...         "deal with increment 7\\n"
        ...         "cut 8\\n"
        ...         "cut -4\\n"
        ...         "deal with increment 7\\n"
        ...         "cut 3\\n"
        ...         "deal with increment 9\\n"
        ...         "deal with increment 3\\n"
        ...         "cut -1\\n"
        ... ).get_index_cycle(1, 10))
        [2, 5, 4, 1]
        >>> list(ShufflesExtended.parse(
        ...         "deal into new stack\\n"
        ...         "cut -2\\n"
        ...         "deal with increment 7\\n"
        ...         "cut 8\\n"
        ...         "cut -4\\n"
        ...         "deal with increment 7\\n"
        ...         "cut 3\\n"
        ...         "deal with increment 9\\n"
        ...         "deal with increment 3\\n"
        ...         "cut -1\\n"
        ... ).get_index_cycle(3, 10))
        [8, 3]
        """
        if max_count is None:
            max_count = size
        search_index = index
        for step in range(max_count):
            search_index = self.get_index_at_position_after_shuffle(
                search_index, size)
            yield search_index
            if search_index == index:
                break
            debugger.default_report_if("Looking...")

    def get_index_at_position_after_shuffle_many(
        self, index, size, count, debugger: Debugger = Debugger(enabled=False),
    ):
        total_index = index
        shuffles = [
            shuffle.make_get_index_at_position_after_shuffle(size)
            for shuffle in reversed(self.shuffles)
        ]
        for step in debugger.stepping(range(count)):
            for shuffle in shuffles:
                total_index = shuffle(total_index)
            if total_index == index:
                break
            debugger.default_report_if(
                f"Looking {int(step / count * 10000) / 100}% "
                f"(current is {total_index})..."
            )
        else:
            return total_index

        cycle_length = step + 1
        debugger.default_report(f"Found cycle of length {cycle_length}")

        for _ in debugger.stepping(range(count % cycle_length)):
            for shuffle in shuffles:
                total_index = shuffle(total_index)
            debugger.default_report_if(
                f"Finishing after cycle (current is {total_index})..."
            )

        return total_index

    def get_index_at_position_after_shuffle(self, index, size):
        """
        >>> # noinspection PyUnresolvedReferences
        >>> tuple(
        ...     ShufflesExtended.parse(
        ...         "deal into new stack\\n"
        ...         "cut -2\\n"
        ...         "deal with increment 7\\n"
        ...         "cut 8\\n"
        ...         "cut -4\\n"
        ...         "deal with increment 7\\n"
        ...         "cut 3\\n"
        ...         "deal with increment 9\\n"
        ...         "deal with increment 3\\n"
        ...         "cut -1\\n"
        ...     ).get_index_at_position_after_shuffle(_index, 10)
        ...     for _index in range(10)
        ... )
        (9, 2, 5, 8, 1, 4, 7, 0, 3, 6)
        """
        total_index = index
        for shuffle in self.reverse_shuffles:
            total_index = shuffle.get_index_at_position_after_shuffle(
                total_index, size)

        return total_index


class ShuffleExtended(part_a.Shuffle, ABC):
    shuffle_classes = {}

    @classmethod
    def override(cls, shuffle_class):
        return cls.register(shuffle_class, override=True)

    def shuffle_deck(self, deck):
        """
        >>> ShufflesExtended.parse('''
        ...     deal with increment 7
        ...     deal into new stack
        ...     deal into new stack
        ... ''').shuffle_deck(tuple(range(10)))
        (0, 3, 6, 9, 2, 5, 8, 1, 4, 7)
        >>> ShufflesExtended.parse('''
        ...     cut 6
        ...     deal with increment 7
        ...     deal into new stack
        ... ''').shuffle_deck(tuple(range(10)))
        (3, 0, 7, 4, 1, 8, 5, 2, 9, 6)
        >>> ShufflesExtended.parse('''
        ...     deal with increment 7
        ...     deal with increment 9
        ...     cut -2
        ... ''').shuffle_deck(tuple(range(10)))
        (6, 3, 0, 7, 4, 1, 8, 5, 2, 9)
        >>> ShufflesExtended.parse('''
        ...     deal into new stack
        ...     cut -2
        ...     deal with increment 7
        ...     cut 8
        ...     cut -4
        ...     deal with increment 7
        ...     cut 3
        ...     deal with increment 9
        ...     deal with increment 3
        ...     cut -1
        ... ''').shuffle_deck(tuple(range(10)))
        (9, 2, 5, 8, 1, 4, 7, 0, 3, 6)
        """
        return tuple(
            deck[self.get_index_at_position_after_shuffle(_index, len(deck))]
            for _index in range(len(deck))
        )

    def get_index_at_position_after_shuffle(self, index: int, size: int) -> int:
        return self.make_get_index_at_position_after_shuffle(size)(index)

    def make_get_index_at_position_after_shuffle(
        self, size: int,
    ) -> Callable[[int], int]:
        raise NotImplementedError

    def to_modulo_shuffle_for_size(self, size: int) -> "ModuloShuffle":
        raise NotImplementedError()


ShufflesExtended.shuffle_class = ShuffleExtended


@ShuffleExtended.override
class DealWithIncrementShuffleExtended(
        ShuffleExtended, part_a.DealWithIncrementShuffle):
    def make_get_index_at_position_after_shuffle(
        self, size: int,
    ) -> Callable[[int], int]:
        """
        >>> DealWithIncrementShuffleExtended(3).shuffle_deck(tuple(range(7)))
        (0, 5, 3, 1, 6, 4, 2)
        >>> # noinspection PyUnresolvedReferences
        >>> tuple(
        ...     DealWithIncrementShuffleExtended(3)
        ...     .get_index_at_position_after_shuffle(_index, 7)
        ...     for _index in range(7)
        ... )
        (0, 5, 3, 1, 6, 4, 2)
        """
        increment = self.increment
        factor = pow(increment, -1, size)

        def get_index_at_position_after_shuffle(index):
            return (index * factor) % size
            # return (index * factor + 0) % size

        return get_index_at_position_after_shuffle

    def to_modulo_shuffle_for_size(self, size: int) -> "ModuloShuffle":
        """
        >>> DealWithIncrementShuffleExtended(3)\\
        ...     .to_modulo_shuffle_for_size(7)\\
        ...     .shuffle_deck(tuple(range(7)))
        (0, 5, 3, 1, 6, 4, 2)
        """
        return ModuloShuffle(
            factor=pow(self.increment, -1, size),
            offset=0,
            size=size,
        )


@ShuffleExtended.override
class CutShuffleExtended(
        ShuffleExtended, part_a.CutShuffle):
    def make_get_index_at_position_after_shuffle(
        self, size: int,
    ) -> Callable[[int], int]:
        """
        >>> CutShuffleExtended(3).shuffle_deck(tuple(range(10)))
        (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)
        >>> CutShuffleExtended(-7).shuffle_deck(tuple(range(10)))
        (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)
        >>> CutShuffleExtended(-4).shuffle_deck(tuple(range(10)))
        (6, 7, 8, 9, 0, 1, 2, 3, 4, 5)
        >>> # noinspection PyUnresolvedReferences
        >>> tuple(
        ...     CutShuffleExtended(3)
        ...     .get_index_at_position_after_shuffle(_index, 10)
        ...     for _index in range(10)
        ... )
        (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)
        >>> # noinspection PyUnresolvedReferences
        >>> tuple(
        ...     CutShuffleExtended(-7)
        ...     .get_index_at_position_after_shuffle(_index, 10)
        ...     for _index in range(10)
        ... )
        (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)
        >>> # noinspection PyUnresolvedReferences
        >>> tuple(
        ...     CutShuffleExtended(-4)
        ...     .get_index_at_position_after_shuffle(_index, 10)
        ...     for _index in range(10)
        ... )
        (6, 7, 8, 9, 0, 1, 2, 3, 4, 5)
        """
        count = self.count

        def get_index_at_position_after_shuffle(index):
            return (index + count) % size
            # return (index * 1 + count) % size

        return get_index_at_position_after_shuffle

    def to_modulo_shuffle_for_size(self, size: int) -> "ModuloShuffle":
        """
        >>> CutShuffleExtended(3)\\
        ...     .to_modulo_shuffle_for_size(10)\\
        ...     .shuffle_deck(tuple(range(10)))
        (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)
        """
        return ModuloShuffle(
            factor=1,
            offset=self.count,
            size=size,
        )


@ShuffleExtended.override
class DealIntoNewStackShuffleExtended(
        ShuffleExtended, part_a.DealIntoNewStackShuffle):
    def make_get_index_at_position_after_shuffle(
        self, size: int,
    ) -> Callable[[int], int]:
        """
        >>> DealIntoNewStackShuffleExtended().shuffle_deck(tuple(range(10)))
        (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        >>> # noinspection PyUnresolvedReferences
        >>> tuple(
        ...     DealIntoNewStackShuffleExtended()
        ...     .get_index_at_position_after_shuffle(_index, 10)
        ...     for _index in range(10)
        ... )
        (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        """
        def get_index_at_position_after_shuffle(index):
            return size - index - 1
            # return (index * (-1) + size - 1) % size

        return get_index_at_position_after_shuffle

    def to_modulo_shuffle_for_size(self, size: int) -> "ModuloShuffle":
        """
        >>> DealIntoNewStackShuffleExtended()\\
        ...     .to_modulo_shuffle_for_size(10)\\
        ...     .shuffle_deck(tuple(range(10)))
        (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        """
        return ModuloShuffle(
            factor=-1,
            offset=size - 1,
            size=size,
        )


Deck = Tuple[int, ...]


@dataclass
class ModuloShuffle:
    factor: int
    offset: int
    size: int

    @classmethod
    def from_shuffle_for_size(
        cls, shuffle: ShuffleExtended, size: int,
    ) -> "ModuloShuffle":
        return shuffle.to_modulo_shuffle_for_size(size)

    def shuffle_deck(self, deck: Deck) -> Deck:
        return tuple(
            deck[self.get_index_at_position_after_shuffle(_index)]
            for _index in range(len(deck))
        )

    def shuffle_deck_with_other(
        self, other: "ModuloShuffle", deck: Deck,
    ) -> Deck:
        """
        >>> def check(lhs: ShuffleExtended, rhs: ShuffleExtended):
        ...     _deck = tuple(range(10))
        ...     with_modulo = lhs\\
        ...         .to_modulo_shuffle_for_size(10)\\
        ...         .shuffle_deck_with_other(
        ...             rhs.to_modulo_shuffle_for_size(10),
        ...             _deck,
        ...         )
        ...     without_modulo = rhs.shuffle_deck(lhs.shuffle_deck(_deck))
        ...     if with_modulo != without_modulo:
        ...         print(without_modulo)
        ...         print(with_modulo)
        ...     return with_modulo == without_modulo
        >>> check(
        ...     DealWithIncrementShuffleExtended(7),
        ...     DealIntoNewStackShuffleExtended(),
        ... )
        True
        """
        def get_index_at_position_after_shuffle_with_other(index):
            index = (index * other.factor + other.offset) % other.size
            return (index * self.factor + self.offset) % self.size

        return tuple(
            deck[get_index_at_position_after_shuffle_with_other(_index)]
            for _index in range(len(deck))
        )

    def get_index_at_position_after_shuffle_many(
        self, index, count, debugger: Debugger = Debugger(enabled=False),
    ):
        return (self.__mul__(count, debugger=debugger))\
            .get_index_at_position_after_shuffle(index)

    def get_index_at_position_after_shuffle(self, index: int) -> int:
        return (index * self.factor + self.offset) % self.size

    def __add__(
        self, other: "ModuloShuffle",
        debugger: Debugger = Debugger(enabled=False),
    ) -> "ModuloShuffle":
        """
        >>> ShufflesExtended.parse('''
        ...     deal with increment 7
        ...     deal into new stack
        ...     deal into new stack
        ... ''').to_modulo_shuffle_for_size(10).shuffle_deck(tuple(range(10)))
        (0, 3, 6, 9, 2, 5, 8, 1, 4, 7)
        >>> ShufflesExtended.parse('''
        ...     cut 6
        ...     deal with increment 7
        ...     deal into new stack
        ... ''').to_modulo_shuffle_for_size(10).shuffle_deck(tuple(range(10)))
        (3, 0, 7, 4, 1, 8, 5, 2, 9, 6)
        >>> ShufflesExtended.parse('''
        ...     deal with increment 7
        ...     deal with increment 9
        ...     cut -2
        ... ''').to_modulo_shuffle_for_size(10).shuffle_deck(tuple(range(10)))
        (6, 3, 0, 7, 4, 1, 8, 5, 2, 9)
        >>> ShufflesExtended.parse(
        ...     "deal into new stack\\n"
        ...     "cut -2\\n"
        ...     "deal with increment 7\\n"
        ...     "cut 8\\n"
        ...     "cut -4\\n"
        ...     "deal with increment 7\\n"
        ...     "cut 3\\n"
        ...     "deal with increment 9\\n"
        ...     "deal with increment 3\\n"
        ...     "cut -1\\n"
        ... ).to_modulo_shuffle_for_size(10).shuffle_deck(tuple(range(10)))
        (9, 2, 5, 8, 1, 4, 7, 0, 3, 6)
        """
        if self.size != other.size:
            raise Exception(f"Cannot combine shuffles with different sizes")

        debugger.report(f"Add {self} + {other}")

        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            factor=(other.factor * self.factor) % self.size,
            offset=(other.offset * self.factor + self.offset) % self.size,
            size=self.size,
        )

    def __mul__(
        self, count: int, debugger: Debugger = Debugger(enabled=False),
    ) -> "ModuloShuffle":
        cls = type(self)
        if count < 0:
            raise Exception(f"Cannot calculate negative count shuffle")

        # noinspection PyArgumentList
        total = cls(
            factor=1,
            offset=0,
            size=self.size,
        )
        power_shuffle = self
        power = 1
        remaining_count = count
        debugger.default_report(
            f"Remaining {math.ceil(math.log2(remaining_count))} rounds "
            f"({remaining_count}, {bin(remaining_count)})"
        )
        while debugger.step_if(remaining_count):
            debugger.default_report_if(
                f"Remaining {math.ceil(math.log2(remaining_count))} rounds "
                f"({remaining_count}, {bin(remaining_count)})"
            )
            if remaining_count % 2:
                total = total + power_shuffle
            remaining_count //= 2
            power *= 2
            power_shuffle = power_shuffle + power_shuffle

        return total


Challenge.main()
challenge = Challenge()
