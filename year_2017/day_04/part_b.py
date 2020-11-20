#!/usr/bin/env python3
import utils
from year_2017.day_04 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        265
        """
        return PhraseSetExtended.from_phrases_text(_input)\
            .get_anagram_valid_count()


class PhraseSetExtended(part_a.PhraseSet):
    def get_anagram_valid_count(self):
        return utils.helper.iterable_length(filter(
            None, map(self.phrase_class.is_anagram_valid, self.phrases)))


class PhraseExtended(part_a.Phrase):
    def is_anagram_valid(self):
        """
        >>> PhraseExtended.from_phrase_text('abcde fghij').is_anagram_valid()
        True
        >>> PhraseExtended.from_phrase_text(
        ...     'abcde xyz ecdab').is_anagram_valid()
        False
        >>> PhraseExtended.from_phrase_text(
        ...     'a ab abc abd abf abj').is_anagram_valid()
        True
        >>> PhraseExtended.from_phrase_text(
        ...     'iiii oiii ooii oooi oooo').is_anagram_valid()
        True
        >>> PhraseExtended.from_phrase_text(
        ...     'oiii ioii iioi iiio').is_anagram_valid()
        False
        """
        return len(self.words) == len(set(map(tuple, map(sorted, self.words))))


PhraseSetExtended.phrase_class = PhraseExtended


challenge = Challenge()
challenge.main()
