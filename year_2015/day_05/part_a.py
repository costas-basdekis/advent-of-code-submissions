#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Generic, Type, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, get_windows, TV, get_type_argument_class, \
    helper


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        255
        """
        return StringSet.from_strings_text(_input).get_nice_string_count()


StringT = TV['String']


@dataclass
class StringSet(Generic[StringT]):
    strings: List[StringT]

    @classmethod
    def get_string_class(cls) -> Type[StringT]:
        return get_type_argument_class(cls, StringT)

    @classmethod
    def from_strings_text(cls, strings_text: str):
        """
        >>> StringSet.from_strings_text("jchzalrnumimnmhp\\nugknbfddgicrmopn")
        StringSet(strings=[String(string='jchzalrnumimnmhp'),
            String(string='ugknbfddgicrmopn')])
        """
        string_class = cls.get_string_class()
        return cls(list(map(string_class, strings_text.splitlines())))

    def get_nice_string_count(self) -> int:
        """
        >>> StringSet.from_strings_text(
        ...     "jchzalrnumimnmhp\\nugknbfddgicrmopn").get_nice_string_count()
        1
        """
        return helper.iterable_length(self.get_nice_strings())

    def get_nice_strings(self) -> Iterable[StringT]:
        """
        >>> list(StringSet.from_strings_text(
        ...     "jchzalrnumimnmhp\\nugknbfddgicrmopn").get_nice_strings())
        [String(string='ugknbfddgicrmopn')]
        """
        return (
            string
            for string in self.strings
            if string.is_nice()
        )


@dataclass
class String:
    string: str

    VOWELS = 'aeiou'
    FORBIDDEN_STRINGS = ['ab', 'cd', 'pq', 'xy']

    def is_nice(self) -> bool:
        """
        >>> String("ugknbfddgicrmopn").is_nice()
        True
        >>> String("aaa").is_nice()
        True
        >>> String("jchzalrnumimnmhp").is_nice()
        False
        >>> String("haegwjzuvuyypxyu").is_nice()
        False
        >>> String("dvszwmarrgswjxmb").is_nice()
        False
        """
        return (
            self.contains_at_least_3_vowels()
            and self.at_least_one_letter_twice_in_a_row()
            and self.does_not_contain_forbidden_strings()
        )

    def contains_at_least_3_vowels(self) -> bool:
        """
        >>> String("aei").contains_at_least_3_vowels()
        True
        >>> String("xazegov").contains_at_least_3_vowels()
        True
        >>> String("aeiouaeiouaeiou").contains_at_least_3_vowels()
        True
        >>> String("dvszwmarrgswjxmb").contains_at_least_3_vowels()
        False
        """
        vowel_count = 0
        for content in self.string:
            if content in self.VOWELS:
                vowel_count += 1
                if vowel_count >= 3:
                    return True

        return False

    def at_least_one_letter_twice_in_a_row(self) -> bool:
        """
        >>> String("xx").at_least_one_letter_twice_in_a_row()
        True
        >>> String("abcdde").at_least_one_letter_twice_in_a_row()
        True
        >>> String("aabbccdd").at_least_one_letter_twice_in_a_row()
        True
        >>> String("jchzalrnumimnmhp").at_least_one_letter_twice_in_a_row()
        False
        """
        for first, second in get_windows(self.string, 2):
            if first == second:
                return True

        return False

    def does_not_contain_forbidden_strings(self) -> bool:
        """
        >>> String("haegwjzuvuyypxyu").does_not_contain_forbidden_strings()
        False
        """
        return not any(map(self.string.__contains__, self.FORBIDDEN_STRINGS))


Challenge.main()
challenge = Challenge()
