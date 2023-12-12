#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from itertools import groupby
from typing import Any, Dict, Iterable, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples, make_and_show_string_table, parse_map_points


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1327
        """
        return Racetrack.from_text(_input).get_duration_save_count_with_cheats(100)

    def play(self):
        racetrack = Racetrack.from_text("""
            ###############
            #...#...#.....#
            #.#.#.#.#.###.#
            #S#...#.#.#...#
            #######.#.#.###
            #######.#.#...#
            #######.#.###.#
            ###..E#...#...#
            ###.#######.###
            #...###...#...#
            #.#####.#.###.#
            #.#...#.#.#...#
            #.#.#.#.#.#.###
            #...#...#...###
            ###############
        """)
        print(racetrack.show(distance_map=racetrack.get_distance_map(racetrack.start)))


@dataclass
class Racetrack:
    walls: Set[Point2D]
    start: Point2D
    end: Point2D

    @classmethod
    def from_text(cls, text: str) -> "Racetrack":
        """
        >>> print(Racetrack.from_text('''
        ...     ###############
        ...     #...#...#.....#
        ...     #.#.#.#.#.###.#
        ...     #S#...#.#.#...#
        ...     #######.#.#.###
        ...     #######.#.#...#
        ...     #######.#.###.#
        ...     ###..E#...#...#
        ...     ###.#######.###
        ...     #...###...#...#
        ...     #.#####.#.###.#
        ...     #.#...#.#.#...#
        ...     #.#.#.#.#.#.###
        ...     #...#...#...###
        ...     ###############
        ... '''))
        ###############
        #...#...#.....#
        #.#.#.#.#.###.#
        #S#...#.#.#...#
        #######.#.#.###
        #######.#.#...#
        #######.#.###.#
        ###..E#...#...#
        ###.#######.###
        #...###...#...#
        #.#####.#.###.#
        #.#...#.#.#...#
        #.#.#.#.#.#.###
        #...#...#...###
        ###############
        """
        walls, starts, ends = parse_map_points(text, ["#", "S", "E"])
        start, = starts
        end, = ends
        return cls(walls=walls, start=start, end=end)

    def __str__(self) -> str:
        return self.show()

    def show(self, distance_map: Optional[Dict[Point2D, int]] = None) -> str:
        if distance_map:
            def show_point(point: Point2D) -> Any:
                if point in distance_map:
                    return distance_map[point]
                return self.show_point(point)
        else:
            show_point = self.show_point
        return make_and_show_string_table(self.walls, show_point, boundaries=self.boundaries)

    def show_point(self, point: Point2D) -> str:
        if point == self.start:
            return "S"
        if point == self.end:
            return "E"
        if point in self.walls:
            return "#"
        return "."

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.walls)

    def is_within_boundaries(self, point: Point2D) -> bool:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return (
            min_x <= point.x <= max_x
            and min_y <= point.y <= max_y
        )

    def get_duration_save_count_with_cheats(self, min_duration_save: Optional[int] = None) -> int:
        """
        >>> Racetrack.from_text('''
        ...     ###############
        ...     #...#...#.....#
        ...     #.#.#.#.#.###.#
        ...     #S#...#.#.#...#
        ...     #######.#.#.###
        ...     #######.#.#...#
        ...     #######.#.###.#
        ...     ###..E#...#...#
        ...     ###.#######.###
        ...     #...###...#...#
        ...     #.#####.#.###.#
        ...     #.#...#.#.#...#
        ...     #.#.#.#.#.#.###
        ...     #...#...#...###
        ...     ###############
        ... ''').get_duration_save_count_with_cheats(20)
        5
        """
        return sum(
            1
            for duration_save in self.get_duration_saves_with_cheats()
            if min_duration_save is None or duration_save >= min_duration_save
        )

    def get_duration_saves_with_cheats(self, min_duration_save: int = 1, start_distance_map: Optional[Dict[Point2D, int]] = None) -> Iterable[int]:
        """
        >>> [(_duration_save, len(list(items))) for _duration_save, items in groupby(sorted(Racetrack.from_text('''
        ...     ###############
        ...     #...#...#.....#
        ...     #.#.#.#.#.###.#
        ...     #S#...#.#.#...#
        ...     #######.#.#.###
        ...     #######.#.#...#
        ...     #######.#.###.#
        ...     ###..E#...#...#
        ...     ###.#######.###
        ...     #...###...#...#
        ...     #.#####.#.###.#
        ...     #.#...#.#.#...#
        ...     #.#.#.#.#.#.###
        ...     #...#...#...###
        ...     ###############
        ... ''').get_duration_saves_with_cheats()))]
        [(2, 14), (4, 14), (6, 2), (8, 4), (10, 2), (12, 3), (20, 1), (36, 1), (38, 1), (40, 1), (64, 1)]
        """
        if start_distance_map is None:
            start_distance_map = self.get_distance_map(self.start)
        seen = set()
        for position, duration in start_distance_map.items():
            next_duration = duration + 2
            for next_position in position.get_manhattan_neighbours():
                if next_position not in self.walls:
                    continue
                for next_position_2 in next_position.get_manhattan_neighbours():
                    if next_position_2 not in start_distance_map:
                        continue
                    if (next_position, next_position_2) in seen:
                        continue
                    seen.add((next_position, next_position_2))
                    skipped_duration = start_distance_map[next_position_2]
                    duration_save = skipped_duration - next_duration
                    if duration_save < min_duration_save:
                        continue
                    yield duration_save

    def get_distance_map(self, start: Point2D) -> Dict[Point2D, int]:
        queue = [start]
        distance_map = {start: 0}
        while queue:
            position = queue.pop(0)
            distance = distance_map[position]
            for next_position in position.get_manhattan_neighbours():
                if next_position in self.walls:
                    continue
                if next_position in distance_map:
                    continue
                distance_map[next_position] = distance + 1
                queue.append(next_position)
        return distance_map

    def get_shortest_duration_without_cheats(self, start_distance_map: Optional[Dict[Point2D, int]] = None) -> int:
        """
        >>> Racetrack.from_text('''
        ...     ###############
        ...     #...#...#.....#
        ...     #.#.#.#.#.###.#
        ...     #S#...#.#.#...#
        ...     #######.#.#.###
        ...     #######.#.#...#
        ...     #######.#.###.#
        ...     ###..E#...#...#
        ...     ###.#######.###
        ...     #...###...#...#
        ...     #.#####.#.###.#
        ...     #.#...#.#.#...#
        ...     #.#.#.#.#.#.###
        ...     #...#...#...###
        ...     ###############
        ... ''').get_shortest_duration_without_cheats()
        84
        """
        if start_distance_map is None:
            start_distance_map = self.get_distance_map(self.start)
        if self.end not in start_distance_map:
            raise Exception(f"Could not find {self.end} from {self.start}")
        return start_distance_map[self.end]


Challenge.main()
challenge = Challenge()
