#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_07 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        340362529351427
        """
        return CalibrationExtended.from_text(_input).get_viable_calibration_result(debugger=debugger)


class CalibrationExtended(part_a.Calibration["EquationExtended"]):
    pass


class EquationExtended(part_a.Equation):
    @classmethod
    def concatenation(cls, left: int, right: int) -> int:
        """
        >>> EquationExtended.concatenation(12, 345)
        12345
        >>> EquationExtended.from_text("156: 15 6").is_viable()
        True
        >>> CalibrationExtended.from_text('''
        ...     190: 10 19
        ...     3267: 81 40 27
        ...     83: 17 5
        ...     156: 15 6
        ...     7290: 6 8 6 15
        ...     161011: 16 10 13
        ...     192: 17 8 14
        ...     21037: 9 7 18 13
        ...     292: 11 6 16 20
        ... ''').get_viable_calibration_result()
        11387
        """
        return int(f"{left}{right}")

    operators = part_a.Equation.operators + [lambda left, right: EquationExtended.concatenation(left, right)]


Challenge.main()
challenge = Challenge()
