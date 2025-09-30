#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import List, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        183788984
        """
        return Program.from_text(_input).get_mul_sum()


@dataclass
class Program:
    text: str

    @classmethod
    def from_text(cls, text: str) -> "Program":
        return cls(text=text.strip())

    re_mul = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)")

    def get_mul_sum(self) -> int:
        """
        >>> Program\\
        ...     .from_text('xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))')\\
        ...     .get_mul_sum()
        161
        """
        return sum(
            first * second
            for first, second in self.get_mul_operands()
        )

    def get_mul_operands(self) -> List[Tuple[int, int]]:
        """
        >>> Program\\
        ...     .from_text('xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))')\\
        ...     .get_mul_operands()
        [(2, 4), (5, 5), (11, 8), (8, 5)]
        """
        return [
            (int(first_str), int(second_str))
            for first_str, second_str in self.re_mul.findall(self.text)
        ]


Challenge.main()
challenge = Challenge()
