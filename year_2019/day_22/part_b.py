#!/usr/bin/env python3
import math
import time
from abc import ABC

import utils
from year_2019.day_22 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve() < 71271225751690
        True
        """
        shuffles = ShufflesExtended.parse(_input)
        return shuffles.get_index_at_position_after_shuffle_many(
            index=2020,
            size=119315717514047,
            count=101741582076661,
            debug=debug,
        )


class ShufflesExtended(part_a.Shuffles):
    def __init__(self, shuffles):
        super().__init__(shuffles)
        self.reverse_shuffles = list(reversed(self.shuffles))

    def get_shuffling_period(self, size):
        period = 1
        for shuffle in self.shuffles:
            period = math.lcm(period, shuffle.get_shuffling_period(size))

        return period

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

    def get_card_at_position_after_shuffle_many(self, deck, count, index,
                                                debug=False):
        index = self.get_index_for_position_after_many_shuffles(
            index, count, len(deck), debug=debug)
        return deck[index]

    def get_index_for_position_after_many_shuffles(self, index, count, size,
                                                   debug=False):
        cycle = list(self.get_index_cycle(
            index, size, max_count=count, debug=debug))
        return cycle[(count - 1) % len(cycle)]

    def get_index_cycle(self, index, size, max_count=None, debug=False,
                        report_count=10000):
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
        if debug:
            start_time = time.time()
        for step in range(max_count):
            search_index = self.get_index_at_position_after_shuffle(
                search_index, size)
            yield search_index
            if search_index == index:
                break
            if debug and step % report_count == 0:
                end_time = time.time()
                duration = end_time - start_time
                start_time = end_time
                print(
                    step, duration / report_count,
                    duration / report_count * ((size - step) or 1) / 3600)

    def get_index_at_position_after_shuffle_many(self, index, size, count,
                                                 debug=False,
                                                 report_count=100000):
        total_index = index
        shuffles = [
            shuffle.make_get_index_at_position_after_shuffle(size)
            for shuffle in reversed(self.shuffles)
        ]
        for step in range(count):
            for shuffle in shuffles:
                total_index = shuffle(total_index)
            if total_index == index:
                break
            if debug:
                if step % report_count == 0:
                    print(step, f"{100000 * step // count / 1000}%")
        else:
            return total_index

        cycle_length = step + 1
        if debug:
            print(f'Found cycle of length {cycle_length}')

        return self.get_index_at_position_after_shuffle_many(
            2020, size, count=count % cycle_length, debug=debug,
            report_count=report_count)

    def get_index_at_position_after_shuffle(self, index, size):
        """
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
        return tuple(
            deck[self.get_index_at_position_after_shuffle(_index, len(deck))]
            for _index in range(len(deck))
        )

    def get_index_at_position_after_shuffle(self, index, size):
        raise NotImplementedError

    def make_get_index_at_position_after_shuffle(self, size):
        raise NotImplementedError

    def get_shuffling_period(self, size):
        raise NotImplementedError


ShufflesExtended.shuffle_class = ShuffleExtended


@ShuffleExtended.override
class DealWithIncrementShuffleExtended(
        ShuffleExtended, part_a.DealWithIncrementShuffle):
    def get_index_at_position_after_shuffle(self, index, size):
        """
        >>> DealWithIncrementShuffleExtended(3).shuffle_deck(tuple(range(7)))
        (0, 5, 3, 1, 6, 4, 2)
        """
        return (index * pow(self.increment, -1, size)) % size

    def make_get_index_at_position_after_shuffle(self, size):
        increment = self.increment
        factor = pow(increment, -1, size)

        def get_index_at_position_after_shuffle(index):
            return (index * factor) % size

        return get_index_at_position_after_shuffle

    def get_shuffling_period(self, size):
        return size


@ShuffleExtended.override
class CutShuffleExtended(
        ShuffleExtended, part_a.CutShuffle):
    def get_index_at_position_after_shuffle(self, index, size):
        """
        >>> CutShuffleExtended(3).shuffle_deck(tuple(range(10)))
        (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)
        >>> CutShuffleExtended(-7).shuffle_deck(tuple(range(10)))
        (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)
        >>> CutShuffleExtended(-4).shuffle_deck(tuple(range(10)))
        (6, 7, 8, 9, 0, 1, 2, 3, 4, 5)
        """
        return (index + self.count) % size

    def make_get_index_at_position_after_shuffle(self, size):
        count = self.count

        def get_index_at_position_after_shuffle(index):
            return (index + count) % size

        return get_index_at_position_after_shuffle

    def get_shuffling_period(self, size):
        return size // math.gcd((self.count + size) % size, size)


@ShuffleExtended.override
class DealIntoNewStackShuffleExtended(
        ShuffleExtended, part_a.DealIntoNewStackShuffle):
    def get_index_at_position_after_shuffle(self, index, size):
        """
        >>> DealIntoNewStackShuffleExtended().shuffle_deck(tuple(range(10)))
        (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        """
        return size - index - 1

    def make_get_index_at_position_after_shuffle(self, size):
        def get_index_at_position_after_shuffle(index):
            return size - index - 1

        return get_index_at_position_after_shuffle

    def get_shuffling_period(self, size):
        return 2


challenge = Challenge()
challenge.main()
