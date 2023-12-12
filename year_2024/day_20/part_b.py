#!/usr/bin/env python3
from itertools import groupby
from typing import Any, Dict, Iterable, Optional, Tuple, Union

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, make_and_show_string_table
from year_2024.day_20 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        985737
        """
        return RacetrackExtended.from_text(_input)\
            .get_duration_save_count_with_cheats_of_length(20, min_duration_save=100, debugger=debugger)

    def play(self):
        racetrack = RacetrackExtended.from_text("""
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
        start_distance_map = racetrack.get_distance_map(racetrack.start)
        start = racetrack.start
        direction_offsets = {
            '\x1b[A': Point2D(0, -1),
            '\x1b[D': Point2D(-1, 0),
            '\x1b[B': Point2D(0, 1),
            '\x1b[C': Point2D(1, 0),
        }
        mode = "save-distance"
        while True:
            if start in start_distance_map:
                duration_save_map = dict(racetrack.get_duration_saves_per_point_of_length(start, 20, 0, start_distance_map))
            else:
                duration_save_map = {}
            def get_value(point: Point2D) -> Any:
                if mode == "save-distance" and point in duration_save_map:
                    result = click.style(str(duration_save_map[point]), fg="green")
                elif mode == "start-distance" and point in start_distance_map:
                    result = click.style(str(start_distance_map[point]), fg="green")
                else:
                    result = racetrack.show_point(point)
                if point == start:
                    result = click.style(click.unstyle(str(result)), fg="red")
                return result
            print(make_and_show_string_table(racetrack.walls, get_value, min_cell_length=2))
            print(f"{start}")
            while True:
                char = click.getchar()
                if char == "s":
                    mode = "start-distance" if mode == "save-distance" else "save-distance"
                    break
                if char in direction_offsets:
                    start = start.offset(direction_offsets[char])
                    break




class RacetrackExtended(part_a.Racetrack):
    def get_duration_save_count_with_cheats_of_length(self, length: int, min_duration_save: int = 1, start_distance_map: Optional[Dict[Point2D, int]] = None, debugger: Debugger = Debugger(enabled=False)) -> int:
        return sum(
            1
            for _ in self.get_duration_saves_with_cheats_of_length(length, min_duration_save=min_duration_save, start_distance_map=start_distance_map, debugger=debugger)
        )

    def get_duration_saves_with_cheats_of_length(self, length: int, min_duration_save: int = 1, start_distance_map: Optional[Dict[Point2D, int]] = None, debugger: Debugger = Debugger(enabled=False)) -> Iterable[int]:
        """
        >>> _racetrack = RacetrackExtended.from_text('''
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
        ... ''')
        >>> [(_duration_save, len(list(items))) for _duration_save, items in groupby(sorted(_racetrack.get_duration_saves_with_cheats_of_length(2)))]
        [(2, 14), (4, 14), (6, 2), (8, 4), (10, 2), (12, 3), (20, 1), (36, 1), (38, 1), (40, 1), (64, 1)]
        >>> [(_duration_save, len(list(items))) for _duration_save, items in groupby(sorted(_racetrack.get_duration_saves_with_cheats_of_length(20, min_duration_save=50)))]
        [(50, 32), (52, 31), (54, 29), (56, 39), (58, 25), (60, 23), (62, 20), (64, 19), (66, 12), (68, 14), (70, 12), (72, 22), (74, 4), (76, 3)]
        """
        if start_distance_map is None:
            start_distance_map = self.get_distance_map(self.start)
        for index, (start, duration) in debugger.stepping(enumerate(start_distance_map.items())):
            for _, duration_save in self.get_duration_saves_per_point_of_length(start, length, min_duration_save, start_distance_map):
                yield duration_save
            if debugger.should_report():
                debugger.default_report_if(f"Checked {index}/{len(start_distance_map)}")

    def get_duration_saves_per_point_of_length(self, start: Point2D, length: int, min_duration_save: int, start_distance_map: Dict[Point2D, int]) -> Iterable[Tuple[Point2D, int]]:
            duration = start_distance_map[start]
            queue = [(start, length)]
            seen = {start}
            while queue:
                position, remaining_length = queue.pop(0)
                next_remaining_length = remaining_length - 1
                for next_position in position.get_manhattan_neighbours():
                    if not self.is_within_boundaries(next_position):
                        continue
                    # if remaining_length == length and next_position not in self.walls:
                    #     continue
                    if next_position in seen:
                        continue
                    seen.add(next_position)
                    if next_position in start_distance_map:
                        next_duration = start_distance_map[next_position]
                        duration_save = next_duration - (duration + length - next_remaining_length)
                        if duration_save >= min_duration_save:
                            yield next_position, duration_save
                    if next_remaining_length == 0:
                        continue
                    queue.append((next_position, next_remaining_length))


Challenge.main()
challenge = Challenge()
