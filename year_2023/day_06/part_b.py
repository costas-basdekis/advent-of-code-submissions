#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_06.part_a import RaceSheet, RaceRecord


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        30565288
        """
        return RaceSheetExtended.from_sheet_text(_input).get_margin_of_error()


class RaceSheetExtended(RaceSheet[RaceRecord]):
    @classmethod
    def from_sheet_text(cls, sheet_text: str) -> "RaceSheet":
        """
        >>> race_sheet = RaceSheetExtended.from_sheet_text('''
        ...     Time:      7  15   30
        ...     Distance:  9  40  200
        ... ''')
        >>> race_sheet
        RaceSheetExtended(records=[RaceRecord(time=71530, distance=940200)])
        >>> race_sheet.get_margin_of_error()
        71503
        """
        time_line, distance_line = sheet_text.strip().splitlines()
        times_str, = cls.re_time.match(time_line).groups()
        distances_str, = cls.re_distance.match(distance_line).groups()

        race_record_class = cls.get_record_class()
        return cls([
            race_record_class(
                int(times_str.replace(" ", "")),
                int(distances_str.replace(" ", "")),
            ),
        ])


Challenge.main()
challenge = Challenge()
