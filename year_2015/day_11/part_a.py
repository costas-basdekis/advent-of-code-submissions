#!/usr/bin/env python3
import re
import string
from typing import Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, get_windows


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        'cqjxxyzz'
        """
        return Password(_input.strip()).get_next_password(debugger=debugger)


PASSWORD_FORBIDDEN_LETTERS = ['i', 'o', 'l']


class Password(str):
    FORBIDDEN_LETTERS = PASSWORD_FORBIDDEN_LETTERS
    THREE_INCREASING_LETTERS_SEQUENCES = [
        "".join(letters)
        for letters in get_windows(string.ascii_lowercase, 3)
        if not set(letters) & set(PASSWORD_FORBIDDEN_LETTERS)
    ]
    NEXT_LETTER_AND_OVERFLOWED = {
        letter: (next_letter, next_letter == 'a')
        for letter, next_letter in (
            (letter, (
                next_letter
                if next_letter not in PASSWORD_FORBIDDEN_LETTERS else
                alternate_next_letter
            ))
            for letter, next_letter, alternate_next_letter
            in zip(
                tuple(string.ascii_lowercase),
                tuple(string.ascii_lowercase)[1:] + ('a',),
                tuple(string.ascii_lowercase)[2:] + ('a', 'b'),
            )
        )
    }

    re_two_instances_of_two_repeated_letters = re.compile(r"(\w+)\1.*(\w)\2")

    def get_next_password(self, debugger: Debugger = Debugger(enabled=False),
                          ) -> 'Password':
        """
        >>> Password('abcdefgh').get_next_password()
        'abcdffaa'
        >>> Password('ghijklmn').get_next_password()
        'ghjaabcc'
        """
        debugger.reset()
        for password in debugger.stepping(self.get_next_password_candidates()):
            if password.is_valid():
                return password
            debugger.default_report_if(password)

    def get_next_password_candidates(self) -> Iterable['Password']:
        """
        >>> # noinspection PyUnresolvedReferences
        >>> [password for password, _
        ...  in zip(Password('xx').get_next_password_candidates(), range(6))]
        ['xy', 'xz', 'ya', 'yb', 'yc', 'yd']
        """
        current = self
        while True:
            current = current.get_next_password_candidate()
            yield current

    def get_next_password_candidate(self) -> 'Password':
        """
        >>> Password('xx').get_next_password_candidate()
        'xy'
        >>> Password('xy').get_next_password_candidate()
        'xz'
        >>> Password('xz').get_next_password_candidate()
        'ya'
        """
        position = -1
        result = list(self)
        while True:
            letter = result[position]
            next_letter, overflow = self.NEXT_LETTER_AND_OVERFLOWED[letter]
            result[position] = next_letter
            if not overflow:
                break
            position -= 1
            if -position > len(result):
                raise Exception(f"Password overflowed: {''.join(result)}")

        cls = type(self)
        return cls(''.join(result))

    def is_valid(self) -> bool:
        """
        >>> Password('abcdefgh').is_valid()
        False
        >>> Password('abcdffaa').is_valid()
        True
        >>> Password('ghijklmn').is_valid()
        False
        >>> Password('ghjaabcc').is_valid()
        True
        """
        return (
            self.has_three_increasing_letters()
            and self.does_not_include_forbidden_letters()
            and self.contains_two_instances_of_two_repeated_letters()
        )

    def has_three_increasing_letters(self) -> bool:
        """
        >>> Password('hijklmmn').has_three_increasing_letters()
        False
        >>> Password('abbceffg').has_three_increasing_letters()
        False
        """
        return any(
            sequence in self
            for sequence in self.THREE_INCREASING_LETTERS_SEQUENCES
        )

    def does_not_include_forbidden_letters(self) -> bool:
        """
        >>> Password('hijklmmn').does_not_include_forbidden_letters()
        False
        """
        return not any(
            letter in self
            for letter in self.FORBIDDEN_LETTERS
        )

    def contains_two_instances_of_two_repeated_letters(self) -> bool:
        """
        >>> Password('abbceffg')\\
        ...     .contains_two_instances_of_two_repeated_letters()
        True
        >>> Password('abbcegjk')\\
        ...     .contains_two_instances_of_two_repeated_letters()
        False
        """
        return bool(self.re_two_instances_of_two_repeated_letters.findall(self))



Challenge.main()
challenge = Challenge()
