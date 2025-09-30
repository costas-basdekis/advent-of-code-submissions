#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Union, Generic, TypeVar, Type

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        598
        """
        return ReportSet.from_text(_input).get_safe_count()


ReportT = TypeVar("ReportT", bound="Report")


@dataclass
class ReportSet(Generic[ReportT]):
    reports: List[ReportT]

    @classmethod
    def get_report_class(cls) -> Type[ReportT]:
        return get_type_argument_class(cls, ReportT)

    @classmethod
    def from_text(cls, text: str) -> "ReportSet":
        """
        >>> _report_set = ReportSet.from_text('''
        ...     7 6 4 2 1
        ...     1 2 7 8 9
        ...     9 7 6 2 1
        ...     1 3 2 4 5
        ...     8 6 4 4 1
        ...     1 3 6 7 9
        ... ''')
        >>> len(_report_set.reports)
        6
        """
        report_class = cls.get_report_class()
        return cls(reports=list(map(report_class.from_text, text.strip().splitlines())))

    def get_safe_count(self) -> int:
        """
        >>> ReportSet.from_text('''
        ...     7 6 4 2 1
        ...     1 2 7 8 9
        ...     9 7 6 2 1
        ...     1 3 2 4 5
        ...     8 6 4 4 1
        ...     1 3 6 7 9
        ... ''').get_safe_count()
        2
        """
        return sum(
            1
            for report in self.reports
            if report.is_safe()
        )


@dataclass
class Report:
    data: List[int]

    @classmethod
    def from_text(cls, text: str) -> "Report":
        """
        >>> Report.from_text("7 6 4 2 1")
        Report(data=[7, 6, 4, 2, 1])
        """
        return cls(data=list(map(int, text.strip().split(" "))))

    def is_safe(self) -> bool:
        should_be_increasing = self.data[1] > self.data[0]
        for first, second in zip(self.data, self.data[1:]):
            pair_increasing = second > first
            if pair_increasing != should_be_increasing:
                return False
            if not (1 <= abs(first - second) <= 3):
                return False
        return True


Challenge.main()
challenge = Challenge()
