#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_07 import part_a
from year_2022.day_07.part_a import Parser


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        214171
        """
        root = Parser()\
            .parse_output(_input)
        debugger.report("\n".join(
            f"{directory.path}: {directory.get_total_size()}"
            for directory in sorted(
                root.get_directories_that_can_free_enough_space(),
                key=lambda directory: directory.get_total_size(),
            )
        ))
        return root\
            .get_smallest_directory_that_can_free_enough_space()\
            .get_total_size()


Challenge.main()
challenge = Challenge()
