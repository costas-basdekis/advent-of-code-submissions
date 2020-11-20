#!/usr/bin/env python3
from aox.challenge import Debugger

from utils import BaseChallenge, Point2D
from utils.collections_utils import last
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger):
        """
        >>> Challenge().default_solve()
        384
        """
        return MazeSolverExtended(_input.strip())\
            .find_longest_path_length(debugger=debugger)


class MazeSolverExtended(part_a.MazeSolver):
    def find_longest_path_length(
            self, start: Point2D = Point2D(0, 0),
            finish: Point2D = Point2D(3, 3),
            debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> MazeSolverExtended('ihgpwlah').find_longest_path_length()
        370
        >>> MazeSolverExtended('kglvqrro').find_longest_path_length()
        492
        >>> MazeSolverExtended('ulqzkmiv').find_longest_path_length()
        830
        """
        last_path = last(self.find_paths(start, finish, debugger), None)
        if last_path is None:
            raise Exception(f"Could not find a path from {start} to {finish}")

        return len(last_path)


Challenge.main()
challenge = Challenge()
