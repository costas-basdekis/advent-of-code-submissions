#!/usr/bin/env python3
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '7861362411'
        """
        return RecipeBoard().tick_and_get_score(int(_input))


class RecipeBoard(namedtuple("RecipeBoard", ("sequence", "indexes"))):
    INDEXES_INDICATORS = [
        ('(', ')'),
        ('[', ']'),
        ('{', '}'),
        ('<', '>'),
    ]

    OPENING_INDEX_INDICATORS = [
        opening
        for opening, _ in INDEXES_INDICATORS
    ]

    @classmethod
    def from_board_text(cls, board_text):
        """
        >>> RecipeBoard.from_board_text("(3)[7] 1  0 ")
        RecipeBoard(sequence='3710', indexes=(0, 1))
        >>> RecipeBoard.from_board_text(" 3  7  1 [0](1) 0 ")
        RecipeBoard(sequence='371010', indexes=(4, 3))
        """
        if len(board_text) % 3 != 0:
            raise Exception(
                f"Length was not a multiple of 3: {len(board_text)}")
        sequence = tuple(
            int(board_text[index])
            for index in range(1, len(board_text), 3)
        )
        indexes_and_opening_indicators = tuple(
            (index // 3, board_text[index])
            for index in range(0, len(board_text), 3)
            if board_text[index] != ' '
        )
        unknown_opening_indicators = {
            opening_indicator
            for _, opening_indicator in indexes_and_opening_indicators
        } - set(cls.OPENING_INDEX_INDICATORS)
        if unknown_opening_indicators:
            raise Exception(
                f"Unknown opening indicators: {unknown_opening_indicators}")

        indexes = tuple(
            index
            for index, _
            in sorted(indexes_and_opening_indicators,
                      key=cls.by_opening_indicator_index)
        )

        return cls._make(("".join(map(str, sequence)), indexes))

    @classmethod
    def by_opening_indicator_index(cls, index_and_opening_indicator):
        _, opening_indicator = index_and_opening_indicator
        return cls.OPENING_INDEX_INDICATORS.index(opening_indicator)

    # noinspection PyInitNewSignature
    def __new__(cls, sequence='37', indexes=(0, 1)):
        """
        >>> RecipeBoard()
        RecipeBoard(sequence='37', indexes=(0, 1))
        """
        # noinspection PyArgumentList
        return super().__new__(cls, sequence, tuple(indexes))

    def tick_and_get_score(self, count, length=10):
        """
        >>> RecipeBoard().tick_and_get_score(9)
        '5158916779'
        >>> RecipeBoard().tick_and_get_score(5)
        '0124515891'
        >>> RecipeBoard().tick_and_get_score(18)
        '9251071085'
        >>> RecipeBoard().tick_and_get_score(2018)
        '5941429882'
        """
        result = self.tick_many(
            count + length - len(self.sequence), count + length)
        return result.get_score(count, length)

    def get_score(self, count, length=10):
        """
        >>> RecipeBoard.from_board_text(
        ...     " 3  7  1  0 [1] 0  1  2 (4) 5  1  5  8  9  1  6  7  7  9  2 ")\\
        ...     .get_score(9)
        '5158916779'
        >>> RecipeBoard.from_board_text(
        ...     " 3  7  1  0 [1] 0  1  2 (4) 5  1  5  8  9  1  6  7  7  9  2 ")\\
        ...     .get_score(5)
        '0124515891'
        """
        score_items = self.sequence[count:count + length]
        if len(score_items) != length:
            raise Exception(
                f"Not enough items to get {length}-score after {count}: only "
                f"got {len(score_items)} items")
        return score_items

    def tick_many(self, count, min_length=None):
        """
        >>> print(RecipeBoard().tick_many(1).show().rstrip())
        (3)[7] 1  0
        >>> print(RecipeBoard().tick_many(15).show().rstrip())
         3  7  1  0 [1] 0  1  2 (4) 5  1  5  8  9  1  6  7  7  9  2
        """
        result = self
        for _ in range(count):
            if min_length is not None and len(result.sequence) > min_length:
                break
            result = result.tick()

        return result

    def tick(self):
        """
        >>> print(RecipeBoard().tick().show().rstrip())
        (3)[7] 1  0
        """
        next_score = sum(
            int(self.sequence[index])
            for index in self.indexes
        )
        next_sequence = self.sequence + str(next_score)
        next_indexes = tuple(
            (
                index
                + int(self.sequence[index])
                + 1
            ) % len(next_sequence)
            for index in self.indexes
        )
        return self._make((next_sequence, next_indexes))

    def show(self):
        """
        >>> print(RecipeBoard().show())
        (3)[7]
        >>> print(RecipeBoard('3710').show().strip())
        (3)[7] 1  0
        >>> print(RecipeBoard('371010', (4, 3)).show().rstrip())
         3  7  1 [0](1) 0
        """
        if len(self.indexes) > len(self.INDEXES_INDICATORS):
            raise Exception(
                f"Show can only support {len(self.INDEXES_INDICATORS)} "
                f"indexes but there are {len(self.indexes)}")
        return "".join(
            "{indicators[0]}{item}{indicators[1]}".format(
                item=item, indicators=(
                    self.INDEXES_INDICATORS[self.indexes.index(index)]
                    if index in self.indexes else
                    (' ', ' ')
                ))
            for index, item in enumerate(self.sequence)
        )


challenge = Challenge()
challenge.main()
