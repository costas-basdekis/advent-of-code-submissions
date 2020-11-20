#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Iterable, Tuple

from aox.challenge import Debugger
from utils import BaseChallenge, all_possible_combinations, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1638
        """
        return Cupboard.from_jugs_text(_input)\
            .get_subset_count_that_add_up_to(150)


@dataclass
class Cupboard:
    jugs: List[int]

    def __post_init__(self):
        self.jugs = sorted(self.jugs)

    @classmethod
    def from_jugs_text(cls, jugs_text: str):
        """
        >>> Cupboard.from_jugs_text("20\\n15\\n10\\n5\\n5\\n")
        Cupboard(jugs=[5, 5, 10, 15, 20])
        """
        return cls(list(map(int, jugs_text.splitlines())))

    def get_subset_count_that_add_up_to(self, total: int) -> int:
        """
        >>> Cupboard.from_jugs_text("20\\n15\\n10\\n5\\n5\\n")\\
        ...     .get_subset_count_that_add_up_to(25)
        4
        """
        return helper.iterable_length(self.get_subsets_that_add_up_to(total))

    def get_subsets_that_add_up_to(self, total: int,
                                   ) -> Iterable[Tuple[int, ...]]:
        return (
            subset
            for subset in self.get_all_subsets()
            if self.does_subset_add_up_to(subset, total)
        )

    def does_subset_add_up_to(self, subset: Tuple[int, ...], total: int,
                              ) -> bool:
        return sum(subset) == total

    def get_all_subsets(self) -> Iterable[Tuple[int, ...]]:
        """
        >>> sorted(Cupboard([1, 1, 2]).get_all_subsets())
        [(), (1,), (1,), (1, 1), (1, 1, 2), (1, 2), (1, 2), (2,)]
        """
        return all_possible_combinations(self.jugs)


Challenge.main()
challenge = Challenge()
