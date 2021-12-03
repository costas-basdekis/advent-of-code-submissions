#!/usr/bin/env python3
from copy import deepcopy
from itertools import count

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_11.part_a import Grid


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        324
        """
        return GridExtended\
            .from_grid_text(_input)\
            .find_first_synchronised_flash_step_index(debugger)


class GridExtended(Grid):
    def find_first_synchronised_flash_step_index(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> GridExtended.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... ''').find_first_synchronised_flash_step_index()
        195
        """
        grid = deepcopy(self)
        for step_index in debugger.stepping(count(1)):
            debugger.report_if(step_index)
            grid.step()
            if grid.did_all_flash:
                return step_index

        raise Exception("Run out of numbers!")

    @property
    def did_all_flash(self) -> bool:
        """
        >>> GridExtended.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... ''').did_all_flash
        False
        >>> GridExtended.from_grid_text('''
        ...     0000000000
        ...     0000000000
        ...     0000000000
        ...     0000000000
        ...     0000000000
        ...     0000000000
        ...     0000000000
        ...     0000000000
        ...     0000000000
        ...     0000000000
        ... ''').did_all_flash
        True
        """
        return all(
            level == 0
            for line in self.levels
            for level in line
        )


Challenge.main()
challenge = Challenge()
