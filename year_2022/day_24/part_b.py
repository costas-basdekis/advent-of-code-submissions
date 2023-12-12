#!/usr/bin/env python3
from typing import List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2022.day_24 import part_a
from year_2022.day_24.part_a import Direction


class Challenge(BaseChallenge):
    part_a_for_testing = part_a
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        997
        """
        return ValleyExtended.from_valley_map(_input).get_min_steps_to_exit_with_snacks(debugger=debugger)


class ValleyExtended(part_a.Valley):
    def get_min_steps_to_exit_with_snacks(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> _valley = ValleyExtended.from_valley_map('''
        ... #E######
        ... #>>.<^<#
        ... #.<..<<#
        ... #>v.><>#
        ... #<^v^^>#
        ... ######.#
        ... ''')
        >>> _valley.get_min_steps_to_exit_with_snacks()
        54
        """
        path, _ = self.find_shortest_exit_path_with_snacks(debugger=debugger)
        return len(path)

    def find_shortest_exit_path_with_snacks(self, debugger: Debugger = Debugger(enabled=False)) -> Tuple[List[Optional[Direction]], "Valley"]:
        path_to_exit, valley_at_exit = self.find_shortest_exit_path(debugger=debugger)
        path_to_snacks, valley_at_snacks = valley_at_exit.find_shortest_exit_path(target=Point2D(1, 0), debugger=debugger)
        path_to_exit_with_snacks, valley_at_exit_with_snacks = valley_at_snacks.find_shortest_exit_path(debugger=debugger)
        return path_to_exit + path_to_snacks + path_to_exit_with_snacks, valley_at_exit


Challenge.main()
challenge = Challenge()
