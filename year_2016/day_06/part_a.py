#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Iterable

from utils import BaseChallenge, Cls, Self, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'dzqckwsd'
        """
        return Decoder.from_messages_text(_input).decode()


@dataclass
class Decoder:
    messages: List[str]

    @classmethod
    def from_messages_text(cls: Cls['Decoder'], messages_text: str,
                           ) -> Self['Decoder']:
        """
        >>> Decoder.from_messages_text("eedadn\\ndrvtee\\neandsr")
        Decoder(messages=['eedadn', 'drvtee', 'eandsr'])
        """
        return cls(messages_text.strip().splitlines())

    def decode(self) -> str:
        """
        >>> Decoder.from_messages_text(
        ...     "eedadn\\ndrvtee\\neandsr\\nraavrd\\natevrs\\ntsrnev\\n"
        ...     "sdttsa\\nrasrtv\\nnssdts\\nntnada\\nsvetve\\ntesnvt\\n"
        ...     "vntsnd\\nvrdear\\ndvrsen\\nenarar").decode()
        'easter'
        """
        lengths = set(map(len, self.messages))
        if len(lengths) > 1:
            raise Exception(
                f"All messages should have the same length, but got lengths "
                f"{', '.join(map(str, sorted(lengths)))}")
        length, = lengths
        return "".join(map(self.decode_column, range(length)))

    def decode_column(self, position: int) -> str:
        """
        >>> Decoder(messages=['eedadn', 'drvtee', 'eandsr']).decode_column(0)
        'e'
        >>> Decoder(messages=['eedadn', 'drvtee', 'eandsr']).decode_column(5)
        Traceback (most recent call last):
        ...
        Exception: Too many letters (3) were the most common
        """
        column = self.get_column(position)
        return self.get_most_common_letter(column)

    def get_column(self, position: int) -> List[str]:
        """
        >>> Decoder(messages=['eedadn', 'drvtee', 'eandsr']).get_column(0)
        ['e', 'd', 'e']
        >>> Decoder(messages=['eedadn', 'drvtee', 'eandsr']).get_column(5)
        ['n', 'e', 'r']
        """
        return [
            message[position]
            for message in self.messages
        ]

    def get_most_common_letter(self, letters: Iterable[str]) -> str:
        """
        >>> Decoder([]).get_most_common_letter('aaabbcc')
        'a'
        >>> Decoder([]).get_most_common_letter('aaabbbccdd')
        Traceback (most recent call last):
        ...
        Exception: Too many letters (2) were the most common
        """
        letter_counts = {
            letter: len(items)
            for letter, items in helper.group_by(letters).items()
        }
        most_common_count = max(letter_counts.values())
        most_common_letters = [
            letter
            for letter, count in letter_counts.items()
            if count == most_common_count
        ]
        if len(most_common_letters) > 1:
            raise Exception(
                f"Too many letters ({len(most_common_letters)}) were the most "
                f"common")
        most_common_letter, = most_common_letters

        return most_common_letter


Challenge.main()
challenge = Challenge()
