#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Union

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2024.day_06 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1586
        """
        return LabExtended.from_text(_input).get_looping_obstacle_count(debugger=debugger)

    def play(self):
        lab = LabExtended.from_text(self.input)
        obstacles_file_path = Path(__file__).parent / "obstacles.json"
        if not obstacles_file_path.is_file():
            obstacles = list(lab.find_looping_obstacles(debugger=Debugger()))
            print(f"Found {len(obstacles)} looping obstacles")
            obstacles_file_path.write_text(json.dumps(list(map(list, obstacles)), indent=2))
        else:
            obstacles = [Point2D(*coordinates) for coordinates in json.loads(obstacles_file_path.read_text())]
            print(f"Loaded {len(obstacles)} looping obstacles")

        index = -1
        while True:
            if index == -1:
                print(lab.show(
                    path_points=lab.get_path_points(),
                    extra_obstacles=obstacles,
                    style_func=lambda point, text: (
                        click.style(text, fg="green")
                        if point in obstacles else
                        text
                    ),
                ))
                print(f"{len(obstacles)} obstacles found")
            else:
                obstacle = obstacles[index]
                lab_with_obstacle = lab.add_obstacle(obstacle)
                is_loop, path_summary, first_index = lab_with_obstacle.get_looping_path_summary()
                if first_index is not None:
                    looping_path_summary = path_summary[first_index:]
                    looping_path_points = lab_with_obstacle.get_path_points(looping_path_summary)
                else:
                    looping_path_summary = []
                    looping_path_points = set()
                print(lab.show(
                    path_points=lab_with_obstacle.get_path_points(path_summary=path_summary),
                    extra_obstacles=[obstacle],
                    style_func=lambda point, text: (
                        click.style(text, fg="green")
                        if point == obstacle else
                        click.style(text, fg="red")
                        if point in looping_path_summary else
                        click.style(text, fg="yellow")
                        if point in looping_path_points else
                        text
                    ),
                ))
                print(f"Is loop at index #{index}: {is_loop}{f', of length {len(looping_path_points)}' if looping_path_points else ''}")
            index = click.prompt(f"Choose next obstacle [0-{len(obstacles)}] or -1 to see all", type=int)


class LabExtended(part_a.Lab):
    def add_obstacle(self, obstacle: Point2D) -> "LabExtended":
        return LabExtended(
            obstacles=self.obstacles | {obstacle},
            guard_position=self.guard_position,
            guard_direction=self.guard_direction,
        )

    def get_looping_obstacle_count(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> LabExtended.from_text('''
        ...     ....#.....
        ...     .........#
        ...     ..........
        ...     ..#.......
        ...     .......#..
        ...     ..........
        ...     .#..^.....
        ...     ........#.
        ...     #.........
        ...     ......#...
        ... ''').get_looping_obstacle_count()
        6
        """
        return sum(1 for _ in self.find_looping_obstacles(debugger=debugger))

    def find_looping_obstacles(self, debugger: Debugger = Debugger(enabled=False)) -> Iterable[Point2D]:
        """
        >>> # noinspection PyTypeChecker
        >>> sorted(LabExtended.from_text('''
        ...     ....#.....
        ...     .........#
        ...     ..........
        ...     ..#.......
        ...     .......#..
        ...     ..........
        ...     .#..^.....
        ...     ........#.
        ...     #.........
        ...     ......#...
        ... ''').find_looping_obstacles())
        [Point2D(x=1, y=8), Point2D(x=3, y=6), Point2D(x=3, y=8), Point2D(x=6, y=7), Point2D(x=7, y=7),
            Point2D(x=7, y=9)]
        """
        path_points = self.get_path_points()
        found_count = 0
        for index, point in enumerate(debugger.stepping(path_points)):
            if point == self.guard_position:
                continue
            is_loop, _, _  = self.add_obstacle(point).get_looping_path_summary()
            if is_loop:
                yield point
                found_count += 1
            if debugger.should_report():
                debugger.default_report_if(f"Checked {index + 1}/{len(path_points)}, found {found_count}")

    def get_looping_path_summary(self) -> Tuple[bool, List[Point2D], Optional[int]]:
        """
        >>> LabExtended.from_text('''
        ...     ....#.....
        ...     .........#
        ...     ..........
        ...     ..#.......
        ...     .......#..
        ...     ..........
        ...     .#..^.....
        ...     ........#.
        ...     #.........
        ...     ......#...
        ... ''').add_obstacle(Point2D(3, 6)).get_looping_path_summary()
        (True, [Point2D(x=4, y=6), Point2D(x=4, y=1), Point2D(x=8, y=1), Point2D(x=8, y=6),
            Point2D(x=4, y=6), Point2D(x=4, y=1), Point2D(x=8, y=1)], 2)
        """
        path = [self.guard_position]
        edges = {}
        position, direction = self.guard_position, self.guard_direction
        is_loop = False
        first_index = None
        while True:
            next_position = position.offset(direction.offset)
            if next_position in self.obstacles:
                path.append(position)
                direction = direction.clockwise
                if len(path) > 2:
                    edge = (path[-2], path[-1])
                    if edge in edges:
                        is_loop = True
                        first_index = edges[edge]
                        break
                    edges[edge] = len(path) - 1
            else:
                if not self.is_within_boundaries(next_position):
                    path.append(position)
                    break
                position = next_position
        return is_loop, path, first_index



Challenge.main()
challenge = Challenge()
