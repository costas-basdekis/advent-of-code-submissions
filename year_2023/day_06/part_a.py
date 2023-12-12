#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import cast, Generic, List, Type, Union

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, TV


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1413720
        """
        return RaceSheet.from_sheet_text(_input).get_margin_of_error()


RaceRecordT = TV["RaceRecord"]


@dataclass
class RaceSheet(Generic[RaceRecordT]):
    records: List["RaceRecord"]

    @classmethod
    def get_record_class(cls) -> Type[RaceRecordT]:
        return cast(
            Type[RaceRecordT],
            get_type_argument_class(cls, RaceRecordT),
        )

    re_time = re.compile(r"\s*Time:\s+([\d\s]+)\s*")
    re_distance = re.compile(r"\s*Distance:\s+([\d\s]+)\s*")

    @classmethod
    def from_sheet_text(cls, sheet_text: str) -> "RaceSheet":
        """
        >>> RaceSheet.from_sheet_text('''
        ...     Time:      7  15   30
        ...     Distance:  9  40  200
        ... ''')
        RaceSheet(records=[RaceRecord(time=7, distance=9),
            RaceRecord(time=15, distance=40),
            RaceRecord(time=30, distance=200)])
        """
        time_line, distance_line = sheet_text.strip().splitlines()
        # return time_line, distance_line
        times_str, = cls.re_time.match(time_line).groups()
        distances_str, = cls.re_distance.match(distance_line).groups()

        race_record_class = cls.get_record_class()
        return cls([
            race_record_class(int(time_str), int(distance_str))
            for time_str, distance_str
            in zip(
                filter(None, times_str.split(" ")),
                filter(None, distances_str.split(" ")),
            )
        ])

    def get_margin_of_error(self) -> int:
        """
        >>> RaceSheet.from_sheet_text('''
        ...     Time:      7  15   30
        ...     Distance:  9  40  200
        ... ''').get_margin_of_error()
        288
        """
        margin = 1
        for record in self.records:
            margin *= record.get_distance_beating_option_count()
        return margin


@dataclass
class RaceRecord:
    time: int
    distance: int

    def get_distance_beating_option_count(self) -> int:
        """
        >>> RaceRecord(7, 9).get_distance_beating_option_count()
        4
        """
        return sum(
            1
            for distance in self.get_distance_options()
            if distance > self.distance
        )

    def get_distance_options(self) -> List[int]:
        """
        >>> RaceRecord(7, 9).get_distance_options()
        [0, 6, 10, 12, 12, 10, 6, 0]
        """
        return [
            self.get_distance_for_time(time)
            for time in range(self.time + 1)
        ]

    def get_distance_for_time(self, time: int) -> int:
        return time * (self.time - time)


Challenge.main()
challenge = Challenge()
