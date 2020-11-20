#!/usr/bin/env python3
import re
from dataclasses import dataclass

from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        55
        """
        return StringSetExtended.from_strings_text(_input)\
            .get_nice_string_count()


class StringSetExtended(part_a.StringSet['StringExtended']):
    pass


@dataclass
class StringExtended(part_a.String):
    re_two_letters_repeated = re.compile(r"(\w\w).*\1")
    re_sandwiched_letter = re.compile(r"(\w)\w\1")

    def is_nice(self) -> bool:
        """
        >>> StringExtended("xyxy").is_nice()
        True
        >>> StringExtended("aabcdefgaa").is_nice()
        False
        >>> StringExtended("aaa").is_nice()
        False
        >>> StringExtended("qjhvhtzxzqqjkmpb").is_nice()
        True
        >>> StringExtended("xxyxx").is_nice()
        True
        >>> StringExtended("uurcxstgmygtbstg").is_nice()
        False
        >>> StringExtended("ieodomkazucvgmuy").is_nice()
        False
        """
        return bool(
            self.has_two_letters_repeated()
            and self.has_sandwiched_letter()
        )

    def has_two_letters_repeated(self) -> bool:
        """
        >>> StringExtended("aabcdefgaa").has_two_letters_repeated()
        True
        >>> StringExtended("xyxy").has_two_letters_repeated()
        True
        >>> StringExtended("aabcdefgaa").has_two_letters_repeated()
        True
        >>> StringExtended("aaa").has_two_letters_repeated()
        False
        """
        return bool(self.re_two_letters_repeated.findall(self.string))

    def has_sandwiched_letter(self) -> bool:
        """
        >>> StringExtended("xyx").has_sandwiched_letter()
        True
        >>> StringExtended("abcdefeghi").has_sandwiched_letter()
        True
        >>> StringExtended("aaa").has_sandwiched_letter()
        True
        """
        return bool(self.re_sandwiched_letter.findall(self.string))


Challenge.main()
challenge = Challenge()
