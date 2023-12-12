#!/usr/bin/env python3
from typing import Dict, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Direction
from year_2024.day_16 import part_a
from year_2024.day_16.part_a import Path


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return MazeExtended.from_text(_input).get_best_path_point_count()


class MazeExtended(part_a.Maze):
    def get_best_path_point_count(self) -> int:
        """
        >>> MazeExtended.from_text('''
        ...     ###############
        ...     #.......#....E#
        ...     #.#.###.#.###.#
        ...     #.....#.#...#.#
        ...     #.###.#####.#.#
        ...     #.#.#.......#.#
        ...     #.#.#####.###.#
        ...     #...........#.#
        ...     ###.#.#####.#.#
        ...     #...#.....#.#.#
        ...     #.#.#.###.#.#.#
        ...     #.....#...#.#.#
        ...     #.###.#.#.#.#.#
        ...     #S..#.....#...#
        ...     ###############
        ... ''').get_best_path_point_count()
        45
        >>> MazeExtended.from_text('''
        ...     #################
        ...     #...#...#...#..E#
        ...     #.#.#.#.#.#.#.#.#
        ...     #.#.#.#...#...#.#
        ...     #.#.#.#.###.#.#.#
        ...     #...#.#.#.....#.#
        ...     #.#.#.#.#.#####.#
        ...     #.#...#.#.#.....#
        ...     #.#.#####.#.###.#
        ...     #.#.#.......#...#
        ...     #.#.###.#####.###
        ...     #.#.#...#.....#.#
        ...     #.#.#.#####.###.#
        ...     #.#.#.........#.#
        ...     #.#.#.#########.#
        ...     #S#.............#
        ...     #################
        ... ''').get_best_path_point_count()
        64
        """
        return len(self.get_best_path_points())

    def get_best_path_points(self) -> Set[Point2D]:
        """
        >>> _maze = MazeExtended.from_text('''
        ...     ###############
        ...     #.......#....E#
        ...     #.#.###.#.###.#
        ...     #.....#.#...#.#
        ...     #.###.#####.#.#
        ...     #.#.#.......#.#
        ...     #.#.#####.###.#
        ...     #...........#.#
        ...     ###.#.#####.#.#
        ...     #...#.....#.#.#
        ...     #.#.#.###.#.#.#
        ...     #.....#...#.#.#
        ...     #.###.#.#.#.#.#
        ...     #S..#.....#...#
        ...     ###############
        ... ''')
        >>> print(_maze.show(points=_maze.get_best_path_points()))
        ###############
        #.......#....O#
        #.#.###.#.###O#
        #.....#.#...#O#
        #.###.#####.#O#
        #.#.#.......#O#
        #.#.#####.###O#
        #..OOOOOOOOO#O#
        ###O#O#####O#O#
        #OOO#O....#O#O#
        #O#O#O###.#O#O#
        #OOOOO#...#O#O#
        #O###.#.#.#O#O#
        #O..#.....#OOO#
        ###############
        >>> _maze = MazeExtended.from_text('''
        ...     #################
        ...     #...#...#...#..E#
        ...     #.#.#.#.#.#.#.#.#
        ...     #.#.#.#...#...#.#
        ...     #.#.#.#.###.#.#.#
        ...     #...#.#.#.....#.#
        ...     #.#.#.#.#.#####.#
        ...     #.#...#.#.#.....#
        ...     #.#.#####.#.###.#
        ...     #.#.#.......#...#
        ...     #.#.###.#####.###
        ...     #.#.#...#.....#.#
        ...     #.#.#.#####.###.#
        ...     #.#.#.........#.#
        ...     #.#.#.#########.#
        ...     #S#.............#
        ...     #################
        ... ''')
        >>> print(_maze.show(points=_maze.get_best_path_points()))
        #################
        #...#...#...#..O#
        #.#.#.#.#.#.#.#O#
        #.#.#.#...#...#O#
        #.#.#.#.###.#.#O#
        #OOO#.#.#.....#O#
        #O#O#.#.#.#####O#
        #O#O..#.#.#OOOOO#
        #O#O#####.#O###O#
        #O#O#..OOOOO#OOO#
        #O#O###O#####O###
        #O#O#OOO#..OOO#.#
        #O#O#O#####O###.#
        #O#O#OOOOOOO..#.#
        #O#O#O#########.#
        #O#OOO..........#
        #################
        """
        start_path: Path = [(self.start, Direction.Right, 0)]
        queue: List[Path] = [start_path]
        best_path_by_position: Dict[Tuple[Point2D, Direction], Path] = {(self.start, Direction.Right): start_path}
        alternate_best_paths_by_position: Dict[Tuple[Point2D, Direction], List[Path]] = {(self.start, Direction.Right): []}
        best_path_cost: Optional[int] = None
        while queue:
            path = queue.pop(0)
            position, direction, cost = path[-1]
            path_additions: List[Path] = [
                [(position.offset(direction.offset), direction, cost + 1)],
                [(position, direction.clockwise, cost + 1000)],
                [(position, direction.counter_clockwise, cost + 1000)],
            ]
            for path_addition in path_additions:
                next_position, next_direction, next_cost = path_addition[-1]
                if best_path_cost is not None and next_cost > best_path_cost:
                    continue
                if next_position in self.walls:
                    continue
                next_path = path + path_addition
                if (next_position, next_direction) in best_path_by_position:
                    best_cost = best_path_by_position[(next_position, next_direction)][-1][2]
                    if best_cost == next_cost:
                        alternate_best_paths_by_position[(next_position, next_direction)].append(next_path)
                    if best_cost <= next_cost:
                        continue
                best_path_by_position[(next_position, next_direction)] = next_path
                alternate_best_paths_by_position[(next_position, next_direction)] = []
                if next_position == self.end:
                    if best_path_cost is None or best_path_cost > next_cost:
                        best_path_cost = next_cost
                    continue
                queue.append(next_path)
        best_paths = [
            best_path_by_position.get((self.end, direction))
            for direction in Direction
            if (self.end, direction) in best_path_by_position
        ]
        if not best_paths:
            raise Exception(f"Could not find {self.end} from {self.start}")
        best_path = min(best_paths, key=lambda _path: _path[-1][2])
        best_path_points_and_directions = {
            (point, direction)
            for point, direction, _ in best_path
        }
        while True:
            next_best_path_points_and_directions = {
                (point, direction)
                for previous_point, previous_direction in best_path_points_and_directions
                if (previous_point, previous_direction) in alternate_best_paths_by_position
                for path in alternate_best_paths_by_position[(previous_point, previous_direction)]
                for point, direction, _ in path
            } - best_path_points_and_directions
            if not next_best_path_points_and_directions:
                break
            best_path_points_and_directions |= next_best_path_points_and_directions
        return {
            point
            for point, _ in best_path_points_and_directions
        }


Challenge.main()
challenge = Challenge()
