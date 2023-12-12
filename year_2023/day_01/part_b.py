#!/usr/bin/env python3
import string
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_01.part_a import CalibrationDocument


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        54728
        """
        return CalibrationDocumentExtended.from_document_text(_input).get_value()


class CalibrationDocumentExtended(CalibrationDocument):
    """
    >>> CalibrationDocumentExtended.from_document_text('''
    ...     two1nine
    ...     eightwothree
    ...     abcone2threexyz
    ...     xtwone3four
    ...     4nineeightseven2
    ...     zoneight234
    ...     7pqrstsixteen
    ... ''').get_value()
    281
    """

    spelled_digits_map = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "zero": "0",
    }
    all_digits = list(spelled_digits_map.keys()) + list(string.digits)

    def get_line_value(self, line: str) -> int:
        """
        >>> CalibrationDocumentExtended([]).get_line_value("two1nine")
        29
        >>> CalibrationDocumentExtended([]).get_line_value("eightwothree")
        83
        >>> CalibrationDocumentExtended([]).get_line_value("abcone2threexyz")
        13
        >>> CalibrationDocumentExtended([]).get_line_value("xtwone3four")
        24
        >>> CalibrationDocumentExtended([]).get_line_value("4nineeightseven2")
        42
        >>> CalibrationDocumentExtended([]).get_line_value("zoneight234")
        14
        >>> CalibrationDocumentExtended([]).get_line_value("7pqrstsixteen")
        76
        """
        first_digit_index_map = {
            line.index(digit): self.spelled_digits_map.get(digit, digit)
            for digit in self.all_digits
            if digit in line
        }
        _, first_digit = min(first_digit_index_map.items())
        last_digit_index_map = {
            line.rindex(digit): self.spelled_digits_map.get(digit, digit)
            for digit in self.all_digits
            if digit in line
        }
        _, last_digit = max(last_digit_index_map.items())
        return int(f"{first_digit}{last_digit}")


Challenge.main()
challenge = Challenge()
