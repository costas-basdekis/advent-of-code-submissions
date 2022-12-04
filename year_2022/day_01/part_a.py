#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        66487
        """
        return SnacksList.from_calories_text(_input).get_largest_calories_count()


@dataclass
class SnacksList:
    snacks_list: [[int]]

    @classmethod
    def from_calories_text(cls, calories_text: str) -> "SnacksList":
        """
        >>> SnacksList.from_calories_text(
        ...     "1000\\n2000\\n3000"
        ...     "\\n\\n4000"
        ...     "\\n\\n5000\\n6000"
        ...     "\\n\\n7000\\n8000\\n9000"
        ...     "\\n\\n10000\\n"
        ... )
        SnacksList(snacks_list=[[1000, 2000, 3000], [4000], [5000, 6000],
            [7000, 8000, 9000], [10000]])
        """
        return cls(
            snacks_list=[
                list(map(int, elf_text.splitlines()))
                for elf_text in calories_text.strip().split("\n\n")
            ]
        )

    def get_largest_calories_count(self) -> int:
        """
        >>> SnacksList(snacks_list=[
        ...     [1000, 2000, 3000], [4000], [5000, 6000], [7000, 8000, 9000],
        ...     [10000],
        ... ]).get_largest_calories_count()
        24000
        """
        return max(map(sum, self.snacks_list))


Challenge.main()
challenge = Challenge()
