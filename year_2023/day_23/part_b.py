#!/usr/bin/env python3
from typing import Dict, List, Optional, Union

import pyperclip

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2023.day_23 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> solution = Challenge().default_solve()
        >>> solution
        6710
        """
        return len(IslandExpanded.from_text(_input).get_longest_path_without_slopes(debugger=debugger)) - 1

    def play(self):
        island = IslandExpanded.from_text(self.input)
        paths = island.get_all_single_choice_paths_without_slopes()
        print(island.show(paths=paths))
        print(len(paths))
        graph_text = "\n".join([
            f"p{path[0].x}x{path[0].y} -> p{path[-1].x}x{path[-1].y};"
            for path in paths
        ])
        pyperclip.copy(graph_text)
        print(f"Copied {len(graph_text)} characters to clipboard, paste into https://dreampuf.github.io/GraphvizOnline/")


class IslandExpanded(part_a.Island):
    def get_longest_path_without_slopes(self, start: Optional[Point2D] = None, end: Optional[Point2D] = None, path_graph: Optional[Dict[Point2D, List[List[Point2D]]]] = None, paths: Optional[List[List[Point2D]]] = None, debugger: Debugger = Debugger(enabled=False)) -> List[Point2D]:
        """
        >>> _island = IslandExpanded.from_text(part_a.EXAMPLE_INPUT)
        >>> _longest_path = _island.get_longest_path_without_slopes()
        >>> len(_longest_path) - 1
        154
        >>> print(_island.show(paths=[_longest_path], hide_forest=False))
        #A#####################
        #AAAAAAA#########AAA###
        #######A#########A#A###
        ###AAAAA#.>AAA###A#A###
        ###A#####.#A#A###A#A###
        ###A>...#.#A#AAAAA#AAA#
        ###A###.#.#A#########A#
        ###AAA#.#.#AAAAAAA#AAA#
        #####A#.#.#######A#A###
        #AAAAA#.#.#AAAAAAA#AAA#
        #A#####.#.#A#########A#
        #A#AAA#...#AAA###...>A#
        #A#A#A#######A###.###A#
        #AAA#A>.#...>A>.#.###A#
        #####A#.#.###A#.#.###A#
        #AAAAA#...#AAA#.#.#AAA#
        #A#########A###.#.#A###
        #AAA###AAA#AAA#...#A###
        ###A###A#A###A#####A###
        #AAA#AAA#A#AAA>.#.>A###
        #A###A###A#A###.#.#A###
        #AAAAA###AAA###...#AAA#
        #####################A#
        """
        if path_graph is None:
            path_graph = self.get_path_graph_without_slopes(normal_paths=paths)
        if start is None:
            start = self.start_point
        if end is None:
            end = self.end_point
        return self.get_longest_path(start=start, end=end, path_graph=path_graph, debugger=debugger)

    def get_path_graph_without_slopes(self, normal_paths: Optional[List[List[Point2D]]] = None) -> Dict[Point2D, List[List[Point2D]]]:
        paths = self.get_all_single_choice_paths_without_slopes(normal_paths=normal_paths)
        return self.get_path_graph(paths=paths)

    def get_all_single_choice_paths_without_slopes(self, start: Optional[Point2D] = None, normal_paths: Optional[List[List[Point2D]]] = None) -> List[List[Point2D]]:
        if normal_paths is None:
            normal_paths = self.get_all_single_choice_paths(start=start)
        path_starts = set(path[0] for path in normal_paths)
        path_ends = set(path[-1] for path in normal_paths)
        unique_starts = path_starts - path_ends
        unique_ends = path_ends - path_starts
        reversed_paths: List[List[Point2D]] = [
            path[::-1]
            for path in normal_paths
            if path[0] not in unique_starts
            and path[-1] not in unique_ends
        ]
        return normal_paths + reversed_paths


Challenge.main()
challenge = Challenge()
