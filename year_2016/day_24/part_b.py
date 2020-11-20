#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        724
        """
        layout = part_a.Layout.from_layout_text(_input)
        graph = layout.to_graph()
        if debugger:
            print(graph.show())
        return graph.get_minimum_step_count(
            return_to_start=True, debugger=debugger)


Challenge.main()
challenge = Challenge()
