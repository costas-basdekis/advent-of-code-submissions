#!/usr/bin/env python3
import re
from abc import ABC

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2496
        """
        shuffles = Shuffles.parse(_input)
        deck = tuple(range(10007))
        shuffled = shuffles.shuffle_deck(deck)

        return shuffled.index(2019)


class Shuffles:
    shuffle_class = NotImplemented

    @classmethod
    def parse(cls, text):
        lines = text.splitlines()
        non_empty_lines = filter(None, lines)
        shuffles = list(map(cls.shuffle_class.parse, non_empty_lines))

        return cls(shuffles)

    def __init__(self, shuffles):
        self.shuffles = shuffles

    def shuffle_deck_many(self, deck, count):
        shuffled = deck
        for _ in range(count):
            shuffled = self.shuffle_deck(shuffled)

        return shuffled

    def shuffle_deck(self, deck):
        """
        >>> Shuffles([
        ...     DealIntoNewStackShuffle(),
        ...     DealIntoNewStackShuffle(),
        ... ]).shuffle_deck(tuple(range(10)))
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        >>> Shuffles([
        ...     DealWithIncrementShuffle(7),
        ...     DealIntoNewStackShuffle(),
        ...     DealIntoNewStackShuffle(),
        ... ]).shuffle_deck(tuple(range(10)))
        (0, 3, 6, 9, 2, 5, 8, 1, 4, 7)
        >>> Shuffles([
        ...     CutShuffle(6),
        ...     DealWithIncrementShuffle(7),
        ...     DealIntoNewStackShuffle(),
        ... ]).shuffle_deck(tuple(range(10)))
        (3, 0, 7, 4, 1, 8, 5, 2, 9, 6)
        >>> Shuffles([
        ...     DealWithIncrementShuffle(7),
        ...     DealWithIncrementShuffle(9),
        ...     CutShuffle(-2),
        ... ]).shuffle_deck(tuple(range(10)))
        (6, 3, 0, 7, 4, 1, 8, 5, 2, 9)
        >>> Shuffles([
        ...     DealIntoNewStackShuffle(),
        ...     CutShuffle (-2),
        ...     DealWithIncrementShuffle(7),
        ...     CutShuffle (8),
        ...     CutShuffle (-4),
        ...     DealWithIncrementShuffle(7),
        ...     CutShuffle (3),
        ...     DealWithIncrementShuffle(9),
        ...     DealWithIncrementShuffle(3),
        ...     CutShuffle (-1),
        ... ]).shuffle_deck(tuple(range(10)))
        (9, 2, 5, 8, 1, 4, 7, 0, 3, 6)
        >>> Shuffles.parse(
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
        for shuffle in self.shuffles:
            deck = shuffle.shuffle_deck(deck)

        return deck

    def serialise(self):
        return "".join(
            f"{shuffle.serialise()}\n"
            for shuffle in self.shuffles
        )


class Shuffle:
    name = NotImplemented
    shuffle_classes = {}

    @classmethod
    def register(cls, shuffle_class, override=False):
        name = shuffle_class.name
        class_name = shuffle_class.__name__
        if name is NotImplemented:
            raise Exception(
                f"Class {class_name} did not specify a name")
        existing_shuffle_class = cls.shuffle_classes.get(name)
        if existing_shuffle_class and not override:
            raise Exception(
                f"Class {existing_shuffle_class.__name__} has already defined "
                f"name '{name}': {class_name}")
        cls.shuffle_classes[name] = shuffle_class

        return shuffle_class

    @classmethod
    def parse(cls, text):
        for shuffle_class in cls.shuffle_classes.values():
            success, result = shuffle_class.try_parse(text)
            if success:
                return result

        raise Exception(f"Could not parse '{text}'")

    @classmethod
    def try_parse(cls, text):
        raise NotImplementedError()

    def shuffle_deck(self, deck):
        raise NotImplementedError()

    def serialise(self):
        raise NotImplementedError()


Shuffles.shuffle_class = Shuffle


class RegexParsingShuffle(Shuffle, ABC):
    re_parse = NotImplemented

    @classmethod
    def try_parse(cls, text):
        match = cls.re_parse.match(text)
        if not match:
            return False, None

        # noinspection PyArgumentList
        shuffle = cls(*match.groups())
        return True, shuffle


@Shuffle.register
class DealWithIncrementShuffle(RegexParsingShuffle):
    name = 'deal-with-increment'
    re_parse = re.compile(r"^deal with increment (\d+)$")

    def __init__(self, increment_str):
        self.increment = int(increment_str)

    def __repr__(self):
        return f"{type(self).__name__}({self.increment})"

    def shuffle_deck(self, deck):
        """
        >>> DealWithIncrementShuffle(1).shuffle_deck(tuple(range(10)))
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        >>> DealWithIncrementShuffle(3).shuffle_deck(tuple(range(10)))
        (0, 7, 4, 1, 8, 5, 2, 9, 6, 3)
        >>> DealWithIncrementShuffle(7).shuffle_deck(tuple(range(10)))
        (0, 3, 6, 9, 2, 5, 8, 1, 4, 7)
        >>> DealWithIncrementShuffle(9).shuffle_deck(
        ...     DealWithIncrementShuffle(3).shuffle_deck(
        ...         tuple(range(10)))) == DealWithIncrementShuffle(27)\\
        ...             .shuffle_deck(tuple(range(10)))
        True
        >>> DealWithIncrementShuffle(1).shuffle_deck(tuple(range(7)))
        (0, 1, 2, 3, 4, 5, 6)
        >>> DealWithIncrementShuffle(3).shuffle_deck(tuple(range(7)))
        (0, 5, 3, 1, 6, 4, 2)
        >>> DealWithIncrementShuffle(5).shuffle_deck(tuple(range(7)))
        (0, 3, 6, 2, 5, 1, 4)
        """
        result = [None] * len(deck)
        for index, card in enumerate(deck):
            result[(index * self.increment) % len(deck)] = card

        return tuple(result)

    def serialise(self):
        return f"deal with increment {self.increment}"


@Shuffle.register
class CutShuffle(RegexParsingShuffle):
    name = 'cut'
    re_parse = re.compile(r"^cut (-?\d+)$")

    def __init__(self, count_str):
        self.count = int(count_str)

    def __repr__(self):
        return f"{type(self).__name__}({self.count})"

    def shuffle_deck(self, deck):
        """
        >>> CutShuffle(3).shuffle_deck(tuple(range(10)))
        (3, 4, 5, 6, 7, 8, 9, 0, 1, 2)
        >>> CutShuffle(-4).shuffle_deck(tuple(range(10)))
        (6, 7, 8, 9, 0, 1, 2, 3, 4, 5)
        >>> CutShuffle(3).shuffle_deck(tuple(range(7)))
        (3, 4, 5, 6, 0, 1, 2)
        >>> CutShuffle(-4).shuffle_deck(tuple(range(7)))
        (3, 4, 5, 6, 0, 1, 2)
        """
        return deck[self.count:] + deck[:self.count]

    def serialise(self):
        return f"cut {self.count}"


@Shuffle.register
class DealIntoNewStackShuffle(RegexParsingShuffle):
    name = 'deal-into-new-stack'
    re_parse = re.compile(r"^deal into new stack$")

    def __init__(self):
        pass

    def __repr__(self):
        return f"{type(self).__name__}()"

    def shuffle_deck(self, deck):
        """
        >>> DealIntoNewStackShuffle().shuffle_deck(tuple(range(10)))
        (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        >>> DealIntoNewStackShuffle().shuffle_deck(tuple(range(7)))
        (6, 5, 4, 3, 2, 1, 0)
        """
        return tuple(reversed(deck))

    def serialise(self):
        return f"deal into new stack"


challenge = Challenge()
challenge.main()
