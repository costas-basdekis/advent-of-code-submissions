#!/usr/bin/env python3
from collections import Iterable
from typing import Tuple

from aox.challenge import Debugger
from utils import BaseChallenge, helper
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        17
        """
        return CupboardExtended.from_jugs_text(_input)\
            .get_subset_count_that_add_up_to_with_size(150)


class CupboardExtended(part_a.Cupboard):
    def get_subset_count_that_add_up_to_with_size(self, total: int) -> int:
        """
        >>> CupboardExtended.from_jugs_text("20\\n15\\n10\\n5\\n5\\n")\\
        ...     .get_subset_count_that_add_up_to_with_size(25)
        3
        """
        min_size = self.get_minimum_number_of_containers_that_add_up_to(total)
        return helper.iterable_length(
            self.get_subsets_that_add_up_to_with_size(total, min_size))

    def get_subsets_that_add_up_to_with_size(
            self, total: int, size: int) -> Iterable[Tuple[int, ...]]:
        return (
            subset
            for subset in self.get_subsets_that_add_up_to(total)
            if len(subset) == size
        )

    def get_minimum_number_of_containers_that_add_up_to(
            self, total: int) -> int:
        """
        >>> CupboardExtended.from_jugs_text("20\\n15\\n10\\n5\\n5\\n")\\
        ...     .get_minimum_number_of_containers_that_add_up_to(25)
        2
        """
        return min(map(len, self.get_subsets_that_add_up_to(total)))


Challenge.main()
challenge = Challenge()
