#!/usr/bin/env python3
import string
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, Set, Tuple, Union

import pyperclip

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Direction, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return len(Island.from_text(_input).get_longest_path(debugger=debugger)) - 1

    def play(self):
        island = Island.from_text(self.input)
        paths = island.get_all_single_choice_paths()
        print(island.show(paths=paths))
        print(len(paths))
        graph_text = "\n".join([
            f"p{path[0].x}x{path[0].y} -> p{path[-1].x}x{path[-1].y};"
            for path in paths
        ])
        pyperclip.copy(graph_text)
        print(f"Copied {len(graph_text)} characters to clipboard")


@dataclass
class Island:
    points: Set[Point2D]
    slopes: Dict[Point2D, Direction]

    @classmethod
    def from_text(cls, text: str) -> "Island":
        """
        >>> print(Island.from_text(EXAMPLE_INPUT))
        #.#####################
        #.......#########...###
        #######.#########.#.###
        ###.....#.>.>.###.#.###
        ###v#####.#v#.###.#.###
        ###.>...#.#.#.....#...#
        ###v###.#.#.#########.#
        ###...#.#.#.......#...#
        #####.#.#.#######.#.###
        #.....#.#.#.......#...#
        #.#####.#.#.#########v#
        #.#...#...#...###...>.#
        #.#.#v#######v###.###v#
        #...#.>.#...>.>.#.###.#
        #####v#.#.###v#.#.###.#
        #.....#...#...#.#.#...#
        #.#########.###.#.#.###
        #...###...#...#...#.###
        ###.###.#.###v#####v###
        #...#...#.#.>.>.#.>.###
        #.###.###.#.###.#.#v###
        #.....###...###...#...#
        #####################.#
        """
        lines = list(map(str.strip, text.strip().splitlines()))
        points = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char in ".><^v"
        }
        slopes = {
            Point2D(x, y): Direction.parse(char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char in "><^v"
        }
        return cls(points=points, slopes=slopes)

    def __str__(self, paths: Optional[List[List[Point2D]]] = None, hide_forest: Optional[bool] = None) -> str:
        path_indexes_by_point = {}
        if paths:
            for path_index, path in enumerate(paths):
                for point in path:
                    path_indexes_by_point.setdefault(point, []).append(path_index)
        min_value, max_value = self.boundaries
        if hide_forest is None:
            hide_forest = paths is not None
        return "\n".join(
            "".join(
                "?"
                if len(path_indexes) > 1 else
                string.ascii_uppercase[path_indexes[0] % len(string.ascii_uppercase)]
                if len(path_indexes) == 1 else
                str(direction)
                if direction is not None else
                "."
                if point in self.points else
                ("#" if not hide_forest else " ")
                for x in range(min_value.x - 1, max_value.x + 2)
                for point in [Point2D(x, y)]
                for direction in [self.slopes.get(point)]
                for path_indexes in [path_indexes_by_point.get(point, [])]
            )
            for y in range(min_value.y, max_value.y + 1)
        )

    def show(self, paths: Optional[List[List[Point2D]]] = None, hide_forest: Optional[bool] = None) -> str:
        return self.__str__(paths=paths, hide_forest=hide_forest)

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.points)

    @cached_property
    def start_point(self) -> Point2D:
        top_row_points = [
            point
            for point in self.points
            if point.y == self.boundaries[0].y
        ]
        if len(top_row_points) != 1:
            raise Exception(f"Expected 1 point on top row ({self.boundaries}) but got {len(top_row_points)} ({top_row_points})")
        return top_row_points[0]

    @cached_property
    def end_point(self) -> Point2D:
        bottom_row_points = [
            point
            for point in self.points
            if point.y == self.boundaries[1].y
        ]
        if len(bottom_row_points) != 1:
            raise Exception(f"Expected 1 point on bottom row ({self.boundaries}) but got {len(bottom_row_points)} ({bottom_row_points})")
        return bottom_row_points[0]

    def get_longest_path(self, paths: Optional[List[List[Point2D]]] = None, debugger: Debugger = Debugger(enabled=False)) -> List[Point2D]:
        """
        >>> _island = Island.from_text(EXAMPLE_INPUT)
        >>> _longest_path = _island.get_longest_path()
        >>> print(_island.show([_island.get_longest_path()], hide_forest=False))
        #A#####################
        #AAAAAAA#########...###
        #######A#########.#.###
        ###AAAAA#AAA>.###.#.###
        ###A#####A#A#.###.#.###
        ###AAAAA#A#A#.....#...#
        ###v###A#A#A#########.#
        ###...#A#A#AAAAAAA#...#
        #####.#A#A#######A#.###
        #.....#A#A#AAAAAAA#...#
        #.#####A#A#A#########v#
        #.#...#AAA#AAA###AAAAA#
        #.#.#v#######A###A###A#
        #...#.>.#...>AAA#A###A#
        #####v#.#.###v#A#A###A#
        #.....#...#...#A#A#AAA#
        #.#########.###A#A#A###
        #...###...#...#AAA#A###
        ###.###.#.###v#####A###
        #...#...#.#.>.>.#.>A###
        #.###.###.#.###.#.#A###
        #.....###...###...#AAA#
        #####################A#
        >>> len(_longest_path) - 1
        94
        """
        if paths is None:
            paths = self.get_all_single_choice_paths()
        path_graph = self.get_path_graph(paths)
        unique_starts = set(path_graph) - {path[-1] for paths in path_graph.values() for path in paths}
        if not unique_starts:
            raise Exception(f"There are no starts")
        queue: List[List[Point2D]] = [
            [start]
            for start in unique_starts
        ]
        longest_path: List[Point2D] = queue[0]
        while debugger.step_if(queue):
            path = queue.pop(0)
            next_paths = path_graph.get(path[-1], [])
            for next_path in next_paths:
                if next_path[-1] in path:
                    continue
                next_total_path = path + next_path[1:]
                next_total_length = len(next_total_path)
                if next_total_length > len(longest_path):
                    longest_path = next_total_path
                queue.append(next_total_path)
            if debugger.should_report():
                debugger.default_report_if(f"Queue: {len(queue)}, longest path: {len(longest_path)}")
        return longest_path

    def get_path_graph(self, paths: Optional[List[List[Point2D]]] = None) -> Dict[Point2D, List[List[Point2D]]]:
        if paths is None:
            paths = self.get_all_single_choice_paths()
        graph: Dict[Point2D, List[List[Point2D]]] = {}
        for path in paths:
            graph.setdefault(path[0], []).append(path)
        return graph

    def get_all_single_choice_paths(self, start: Optional[List[Point2D]] = None) -> List[List[Point2D]]:
        """
        >>> _island = Island.from_text(EXAMPLE_INPUT)
        >>> print(_island.show(paths=_island.get_all_single_choice_paths()))
         A
         AAAAAAA         HHH
               A         H H
           AAAAA BB?HH   H H
           A     B D H   H H
           ?BBBB B D HHHHH HHH
           C   B B D         H
           CCC B B DDDDDDD HHH
             C B B       D H
         CCCCC B B DDDDDDD HHH
         C     B B D         H
         C CCC BBB DDD   FFFF?
         C C C       D   F   I
         CCC ?EE EEEE?FF F   I
             K E E   G F F   I
         KKKKK EEE GGG F F III
         K         G   F F I
         KKK   KKK GGG FFF I
           K   K K   G     I
         KKK KKK K KK?LL LL?
         K   K   K K   L L J
         KKKKK   KKK   LLL JJJ
                             J
        """
        if start is None:
            start = [self.start_point]
        queue: List[List[Point2D]] = [start]
        seen: Set[Point2D] = set(start)
        paths: List[List[Point2D]] = []
        while queue:
            start = queue.pop(0)
            path, next_starts = self.get_single_choice_path(start, seen)
            paths.append(path)
            queue.extend([path[-1], next_new_start] for next_new_start in next_starts)
        paths = self.break_paths(paths)
        return paths

    def break_paths(self, paths: List[List[Point2D]]) -> List[List[Point2D]]:
        paths = list(paths)
        while True:
            ends = {
                path[-1]
                for path in paths
            }
            for path in paths:
                overlaps = sorted(set(path[1:-1]) & ends, key=path.index)
                if not overlaps:
                    continue
                paths.remove(path)
                indexes = [0] + list(map(path.index, overlaps)) + [len(path) - 1]
                paths.extend(
                    path[start_index:end_index + 1]
                    for start_index, end_index in zip(indexes, indexes[1:])
                )
                break
            else:
                break
        return paths

    def get_single_choice_path(self, start: List[Point2D], external_seen: Optional[Set[Point2D]] = None) -> Tuple[List[Point2D], List[Point2D]]:
        """
        >>> Island.from_text(EXAMPLE_INPUT).get_single_choice_path([Point2D(1, 0)])
        ([Point2D(x=1, y=0), Point2D(x=1, y=1), ..., Point2D(x=7, y=1), ..., Point2D(x=7, y=3), ..., Point2D(x=3, y=3),
            ..., Point2D(x=3, y=5)], [Point2D(x=4, y=5), Point2D(x=3, y=6)])
        """
        path = list(start)
        internal_seen = set(start)
        while True:
            position = path[-1]
            slope = self.slopes.get(position)
            if slope is not None:
                next_positions: Set[Point2D] = {position.offset(slope.offset)}
            else:
                next_positions: Set[Point2D] = set(position.get_manhattan_neighbours())
            next_positions = (next_positions & self.points) - internal_seen
            next_positions = {
                next_position
                for next_position in next_positions
                for next_slope in [self.slopes.get(next_position)]
                if next_slope is None or next_position == position.offset(next_slope.offset)
            }
            if len(next_positions) != 1:
                break
            next_position, = next_positions
            path.append(next_position)
            internal_seen.add(next_position)
            if external_seen and next_position in external_seen:
                next_positions = set()
                break
        if external_seen:
            external_seen |= internal_seen
        return path, list(next_positions)


EXAMPLE_INPUT = """
#.#####################
#.......#########...###
#######.#########.#.###
###.....#.>.>.###.#.###
###v#####.#v#.###.#.###
###.>...#.#.#.....#...#
###v###.#.#.#########.#
###...#.#.#.......#...#
#####.#.#.#######.#.###
#.....#.#.#.......#...#
#.#####.#.#.#########v#
#.#...#...#...###...>.#
#.#.#v#######v###.###v#
#...#.>.#...>.>.#.###.#
#####v#.#.###v#.#.###.#
#.....#...#...#.#.#...#
#.#########.###.#.#.###
#...###...#...#...#.###
###.###.#.###v#####v###
#...#...#.#.>.>.#.>.###
#.###.###.#.###.#.#v###
#.....###...###...#...#
#####################.#
"""


Challenge.main()
challenge = Challenge()
