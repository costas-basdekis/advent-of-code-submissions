#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Tuple, Type

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        383
        """
        return PhraseSet.from_phrases_text(_input).get_valid_count()


class PhraseSet:
    phrase_class: Type['Phrase']

    @classmethod
    def from_phrases_text(cls, phrases_text):
        return cls(list(map(
            cls.phrase_class.from_phrase_text,
            phrases_text.strip().splitlines())))

    def __init__(self, phrases):
        self.phrases = phrases

    def get_valid_count(self):
        return utils.helper.iterable_length(filter(
            None, map(self.phrase_class.is_valid, self.phrases)))


@dataclass
class Phrase:
    words: Tuple[str]

    @classmethod
    def from_phrase_text(cls, phrase_text):
        """
        >>> Phrase.from_phrase_text('aa bb cc dd ee')
        Phrase(words=('aa', 'bb', 'cc', 'dd', 'ee'))
        """
        return cls(tuple(phrase_text.strip().split(' ')))

    def is_valid(self):
        """
        >>> Phrase.from_phrase_text('aa bb cc dd ee').is_valid()
        True
        >>> Phrase.from_phrase_text('aa bb cc dd aa').is_valid()
        False
        >>> Phrase.from_phrase_text('aa bb cc dd aaa').is_valid()
        True
        """
        return len(self.words) == len(set(self.words))


PhraseSet.phrase_class = Phrase


challenge = Challenge()
challenge.main()
