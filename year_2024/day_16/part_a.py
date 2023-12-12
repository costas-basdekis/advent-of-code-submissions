#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Direction, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        79404
        """
        return Maze.from_text(_input).get_best_path_cost()


Path = List[Tuple[Point2D, Direction, int]]


@dataclass
class Maze:
    walls: Set[Point2D]
    start: Point2D
    end: Point2D

    @classmethod
    def from_text(cls, text: str) -> "Maze":
        """
        >>> print(Maze.from_text('''
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
        ... '''))
        ###############
        #.......#....E#
        #.#.###.#.###.#
        #.....#.#...#.#
        #.###.#####.#.#
        #.#.#.......#.#
        #.#.#####.###.#
        #...........#.#
        ###.#.#####.#.#
        #...#.....#.#.#
        #.#.#.###.#.#.#
        #.....#...#.#.#
        #.###.#.#.#.#.#
        #S..#.....#...#
        ###############
        """
        lines = list(map(str.strip, text.strip().splitlines()))
        walls = {
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char == "#"
        }
        start, = [
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char == "S"
        ]
        end, = [
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char == "E"
        ]
        return cls(walls=walls, start=start, end=end)

    def __str__(self) -> str:
        return self.show()

    def show(self, path: Optional[Path] = None, points: Optional[Set[Point2D]] = None) -> str:
        if path:
            arrows_map = {
                position: str(direction)
                for position, direction, _ in path
            }
        else:
            arrows_map = {}
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return "\n".join(
            "".join(
                "#"
                if point in self.walls else
                "O"
                if points and point in points else
                "S"
                if point == self.start else
                "E"
                if point == self.end else
                arrows_map[point]
                if point in arrows_map else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.walls)

    def get_best_path_cost(self, path: Optional[Path] = None) -> int:
        """
        >>> Maze.from_text('''
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
        ... ''').get_best_path_cost()
        7036
        >>> Maze.from_text('''
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
        ... ''').get_best_path_cost()
        11048
        """
        if path is None:
            path = self.get_best_path()
        _, _, cost = path[-1]
        return cost

    def get_best_path(self) -> Path:
        """
        >>> _maze = Maze.from_text('''
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
        >>> print(_maze.show(path=_maze.get_best_path()))
        ###############
        #.......#....E#
        #.#.###.#.###^#
        #.....#.#...#^#
        #.###.#####.#^#
        #.#.#.......#^#
        #.#.#####.###^#
        #..>>>>>>>>v#^#
        ###^#.#####v#^#
        #>>^#.....#v#^#
        #^#.#.###.#v#^#
        #^....#...#v#^#
        #^###.#.#.#v#^#
        #S..#.....#>>^#
        ###############
        >>> _maze = Maze.from_text('''
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
        >>> print(_maze.show(path=_maze.get_best_path()))
        #################
        #...#...#...#..E#
        #.#.#.#.#.#.#.#^#
        #.#.#.#...#...#^#
        #.#.#.#.###.#.#^#
        #>>v#.#.#.....#^#
        #^#v#.#.#.#####^#
        #^#v..#.#.#>>>>^#
        #^#v#####.#^###.#
        #^#v#..>>>>^#...#
        #^#v###^#####.###
        #^#v#>>^#.....#.#
        #^#v#^#####.###.#
        #^#v#^........#.#
        #^#v#^#########.#
        #S#>>^..........#
        #################
        """
        start_path: Path = [(self.start, Direction.Right, 0)]
        queue: List[Path] = [start_path]
        best_path_by_position = {self.start: start_path}
        while queue:
            path = queue.pop(0)
            position, direction, cost = path[-1]
            path_additions: List[Path] = [
                [(position.offset(direction.offset), direction, cost + 1)],
                [
                    (position, direction.clockwise, cost + 1000),
                    (position.offset(direction.clockwise.offset), direction.clockwise, cost + 1001),
                ],
                [
                    (position, direction.counter_clockwise, cost + 1000),
                    (position.offset(direction.counter_clockwise.offset), direction.counter_clockwise, cost + 1001),
                ],
                [
                    (position, direction.clockwise, cost + 1000),
                    (position, direction.opposite, cost + 2000),
                    (position.offset(direction.opposite.offset), direction.opposite, cost + 2001),
                ],
            ]
            for path_addition in path_additions:
                next_position, next_direction, next_cost = path_addition[-1]
                if next_position in self.walls:
                    continue
                if next_position in best_path_by_position and best_path_by_position[next_position][-1][2] <= next_cost:
                    continue
                next_path = path + path_addition
                best_path_by_position[next_position] = next_path
                if next_position == self.end:
                    continue
                queue.append(next_path)
        if self.end not in best_path_by_position:
            raise Exception(f"Could not find {self.end} from {self.start}")
        return best_path_by_position[self.end]



Challenge.main()
challenge = Challenge()
