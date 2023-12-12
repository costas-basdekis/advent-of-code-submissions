#!/usr/bin/env python3
import re
from typing import List, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_03 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return ProgramExtended.from_text(_input)\
            .get_mul_sum_with_dos()


class ProgramExtended(part_a.Program):
    re_mul_and_do = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)|(do)\(\)|(don't)\(\)")

    def get_mul_sum_with_dos(self) -> int:
        """
        >>> ProgramExtended\\
        ...     .from_text("xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))")\\
        ...     .get_mul_sum_with_dos()
        48
        """
        enabled = True
        total = 0
        for operands_or_enable in self.get_mul_operands_and_dos():
            if isinstance(operands_or_enable, bool):
                enabled = operands_or_enable
            else:
                if enabled:
                    first, second = operands_or_enable
                    total += first * second
        return total

    def get_mul_operands_and_dos(self) -> List[Union[bool, Tuple[int, int]]]:
        """
        >>> ProgramExtended\\
        ...     .from_text("xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))")\\
        ...     .get_mul_operands_and_dos()
        [(2, 4), False, (5, 5), (11, 8), True, (8, 5)]
        """
        return [
            (
                (int(groups[0]), int(groups[1]))
                if groups[0] and groups[1] else
                bool(groups[2])
            )
            for groups in self.re_mul_and_do.findall(self.text)
        ]

Challenge.main()
challenge = Challenge()
