#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_02 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        634
        """
        return ReportSetExtended.from_text(_input)\
            .get_safe_with_1_removal_count()


class ReportSetExtended(part_a.ReportSet["ReportExtended"]):
    def get_safe_with_1_removal_count(self) -> int:
        """
        >>> ReportSetExtended.from_text('''
        ...     7 6 4 2 1
        ...     1 2 7 8 9
        ...     9 7 6 2 1
        ...     1 3 2 4 5
        ...     8 6 4 4 1
        ...     1 3 6 7 9
        ... ''').get_safe_with_1_removal_count()
        4
        """
        return sum(
            1
            for report in self.reports
            if report.is_safe_with_1_removal()
        )


class ReportExtended(part_a.Report):
    def is_safe_with_1_removal(self) -> bool:
        if self.is_safe():
            return True
        cls = type(self)
        for index in range(len(self.data)):
            # noinspection PyArgumentList
            if cls(data=self.data[:index] + self.data[index + 1:]).is_safe():
                return True
        return False


Challenge.main()
challenge = Challenge()
