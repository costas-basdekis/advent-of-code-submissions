#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_09.part_a import Report, Sequence


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1087
        """
        return ReportExtended.from_report_text(_input).predict_previous_sum()


class ReportExtended(Report[Sequence]):
    def predict_previous_sum(self) -> int:
        """
        >>> ReportExtended.from_report_text('''
        ...     0 3 6 9 12 15
        ...     1 3 6 10 15 21
        ...     10 13 16 21 30 45
        ... ''').predict_previous_sum()
        2
        """
        return ReportExtended([
            Sequence(sequence.values[::-1]) for sequence in self.sequences
        ]).predict_next_sum()


Challenge.main()
challenge = Challenge()
