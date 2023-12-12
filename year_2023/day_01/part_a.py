#!/usr/bin/env python3
import string
from dataclasses import dataclass
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        54916
        """
        return CalibrationDocument.from_document_text(_input).get_value()


@dataclass
class CalibrationDocument:
    lines: List[str]

    @classmethod
    def from_document_text(cls, document_text: str) -> "CalibrationDocument":
        """
        >>> CalibrationDocument.from_document_text('''
        ...     1abc2
        ...     pqr3stu8vwx
        ...     a1b2c3d4e5f
        ...     treb7uchet
        ... ''')
        CalibrationDocument(lines=['1abc2', 'pqr3stu8vwx', 'a1b2c3d4e5f',
            'treb7uchet'])
        """
        return cls(
            lines=list(map(str.strip, document_text.strip().splitlines())),
        )

    def get_value(self) -> int:
        """
        >>> CalibrationDocument.from_document_text('''
        ...     1abc2
        ...     pqr3stu8vwx
        ...     a1b2c3d4e5f
        ...     treb7uchet
        ... ''').get_value()
        142
        """
        return sum(map(self.get_line_value, self.lines))

    def get_line_value(self, line: str) -> int:
        """
        >>> CalibrationDocument([]).get_line_value("1abc2")
        12
        >>> CalibrationDocument([]).get_line_value("pqr3stu8vwx")
        38
        >>> CalibrationDocument([]).get_line_value("a1b2c3d4e5f")
        15
        >>> CalibrationDocument([]).get_line_value("treb7uchet")
        77
        """
        digits = [char for char in line if char in string.digits]
        return int(f"{digits[0]}{digits[-1]}")


Challenge.main()
challenge = Challenge()
