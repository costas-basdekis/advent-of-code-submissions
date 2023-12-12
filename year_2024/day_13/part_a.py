#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import ClassVar, List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        36758
        """
        return Arcade.from_text(_input).get_winning_cost()


@dataclass
class Arcade:
    machines: List["Machine"]

    @classmethod
    def from_text(cls, text: str) -> "Arcade":
        """
        >>> len(Arcade.from_text('''
        ...     Button A: X+94, Y+34
        ...     Button B: X+22, Y+67
        ...     Prize: X=8400, Y=5400
        ...
        ...     Button A: X+26, Y+66
        ...     Button B: X+67, Y+21
        ...     Prize: X=12748, Y=12176
        ...
        ...     Button A: X+17, Y+86
        ...     Button B: X+84, Y+37
        ...     Prize: X=7870, Y=6450
        ...
        ...     Button A: X+69, Y+23
        ...     Button B: X+27, Y+71
        ...     Prize: X=18641, Y=10279
        ... ''').machines)
        4
        """
        return cls(machines=list(map(Machine.from_text, text.strip().split("\n\n"))))

    def get_winning_cost(self) -> int:
        """
        >>> Arcade.from_text('''
        ...     Button A: X+94, Y+34
        ...     Button B: X+22, Y+67
        ...     Prize: X=8400, Y=5400
        ...
        ...     Button A: X+26, Y+66
        ...     Button B: X+67, Y+21
        ...     Prize: X=12748, Y=12176
        ...
        ...     Button A: X+17, Y+86
        ...     Button B: X+84, Y+37
        ...     Prize: X=7870, Y=6450
        ...
        ...     Button A: X+69, Y+23
        ...     Button B: X+27, Y+71
        ...     Prize: X=18641, Y=10279
        ... ''').get_winning_cost()
        480
        """
        return sum(
            cost
            for machine in self.machines
            for cost in [machine.get_winning_cost()]
            if cost is not None
        )


@dataclass
class Machine:
    a_offset: Point2D
    b_offset: Point2D
    target: Point2D

    re_machine: ClassVar[re.Pattern] = re.compile(r"^Button A: X\+(\d+), Y\+(\d+)\s*Button B: X\+(\d+), Y\+(\d+)\s*Prize: X=(\d+), Y=(\d+)$", re.MULTILINE)

    @classmethod
    def from_text(cls, text: str) -> "Machine":
        """
        >>> Machine.from_text('''
        ...     Button A: X+94, Y+34
        ...     Button B: X+22, Y+67
        ...     Prize: X=8400, Y=5400
        ... ''')
        Machine(a_offset=Point2D(x=94, y=34), b_offset=Point2D(x=22, y=67), target=Point2D(x=8400, y=5400))
        """
        match = cls.re_machine.match(text.strip())
        if not match:
            raise Exception(f"Could not parse {repr(text)}")
        str_values = match.groups()
        a_x, a_y, b_x, b_y, target_x, target_y = map(int, str_values)
        return cls(
            a_offset=Point2D(a_x, a_y),
            b_offset=Point2D(b_x, b_y),
            target=Point2D(target_x, target_y),
        )

    def get_winning_cost(self) -> Optional[int]:
        """
        >>> Machine.from_text('''
        ...     Button A: X+94, Y+34
        ...     Button B: X+22, Y+67
        ...     Prize: X=8400, Y=5400
        ... ''').get_winning_cost()
        280
        """
        combination = self.get_winning_combination()
        if combination is None:
            return None
        a, b = combination
        return a * 3 + b * 1

    def get_winning_combination(self) -> Optional[Tuple[int, int]]:
        """
        >>> Machine.from_text('''
        ...     Button A: X+94, Y+34
        ...     Button B: X+22, Y+67
        ...     Prize: X=8400, Y=5400
        ... ''').get_winning_combination()
        (80, 40)
        """

        """
        a * ax + b * bx = tx
        a * ay + b * by = ty
        
        a * ax / bx + b = tx / bx
        a * ay / by + b = ty / by
        
        a * (ax / bx - ay / by) = tx / bx - ty / by
        a = (tx / bx - ty / by) / (ax / bx - ay / by)
        
        a + b * bx / ax = tx / ax
        a + b * by / ay = ty / ay
        
        b * (bx / ax - by / ay) = tx / ax - ty / ay
        b = (tx / ax - ty / ay) / (bx / ax - by / ay)
        """
        ax, ay = self.a_offset
        bx, by = self.b_offset
        tx, ty = self.target
        a = (tx / bx - ty / by) / (ax / bx - ay / by)
        b = (tx / ax - ty / ay) / (bx / ax - by / ay)
        int_a, int_b = round(a), round(b)
        a_diff = abs(int_a - a)
        b_diff = abs(int_b - b)
        if a_diff > 0.0001 or b_diff > 0.0001:
            return None
        return int_a, int_b


Challenge.main()
challenge = Challenge()
