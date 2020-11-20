#!/usr/bin/env python3
from collections import Iterable

from utils import BaseChallenge, helper
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'lragovly'
        """
        return DecoderExtended.from_messages_text(_input).decode()


class DecoderExtended(part_a.Decoder):
    """
    >>> DecoderExtended.from_messages_text(
    ...     "eedadn\\ndrvtee\\neandsr\\nraavrd\\natevrs\\ntsrnev\\n"
    ...     "sdttsa\\nrasrtv\\nnssdts\\nntnada\\nsvetve\\ntesnvt\\n"
    ...     "vntsnd\\nvrdear\\ndvrsen\\nenarar").decode()
    'advent'
    """
    def decode_column(self, position: int) -> str:
        """
        >>> DecoderExtended(
        ...     messages=['eedadn', 'drvtee', 'eandsr']).decode_column(0)
        'd'
        >>> DecoderExtended(
        ...     messages=['eedadn', 'drvtee', 'eandsr']).decode_column(5)
        Traceback (most recent call last):
        ...
        Exception: Too many letters (3) were the least common
        """
        column = self.get_column(position)
        return self.get_least_common_letter(column)

    def get_least_common_letter(self, letters: Iterable[str]) -> str:
        """
        >>> DecoderExtended([]).get_least_common_letter('aaabbccd')
        'd'
        >>> DecoderExtended([]).get_least_common_letter('aaabbbccdd')
        Traceback (most recent call last):
        ...
        Exception: Too many letters (2) were the least common
        """
        letter_counts = {
            letter: len(items)
            for letter, items in helper.group_by(letters).items()
        }
        least_common_count = min(letter_counts.values())
        least_common_letters = [
            letter
            for letter, count in letter_counts.items()
            if count == least_common_count
        ]
        if len(least_common_letters) > 1:
            raise Exception(
                f"Too many letters ({len(least_common_letters)}) were the "
                f"least common")
        least_common_letter, = least_common_letters

        return least_common_letter


Challenge.main()
challenge = Challenge()
