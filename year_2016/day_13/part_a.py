#!/usr/bin/env python3
from dataclasses import dataclass, field
from itertools import product
from typing import Dict, Iterable, List, Optional, Type

from aox.utils import Timer

from utils import BaseChallenge, min_and_max_tuples, get_bit_count, Self, \
    Point2D


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        90
        """
        maze = Maze(int(_input))
        solution = maze.solve(Point2D(1, 1), Point2D(31, 39))
        if debug:
            print(maze.show(solution=solution))

        return len(solution) - 1


Position = Point2D


class MazeSolver:
    def get_solution_length(self, maze: 'Maze', start: Position, end: Position,
                            ) -> int:
        """
        >>> MazeSolver().get_solution_length(
        ...     Maze(10).fill(product(range(10), range(7))),
        ...     Point2D(1, 1), Point2D(1, 1))
        0
        >>> MazeSolver().get_solution_length(
        ...     Maze(10).fill(product(range(10), range(7))),
        ...     Point2D(1, 1), Point2D(7, 4))
        11
        >>> MazeSolver().get_solution_length(
        ...     Maze(10), Point2D(1, 1), Point2D(7, 4))
        11
        """
        return len(self.solve(maze, start, end)) - 1

    def solve(self, maze: 'Maze', start: Position, end: Position,
              debug: bool = False) -> List[Position]:
        """
        >>> _maze = Maze(10).fill(product(range(10), range(7)))
        >>> solution = MazeSolver().solve(_maze, Point2D(1, 1), Point2D(7, 4))
        >>> print(_maze.show(solution=solution))
        .#.####.##
        .O#..#...#
        #OOO.##...
        ###O#.###.
        .##OO#.O#.
        ..##OOOO#.
        #...##.###
        >>> bare_maze = Maze(10)
        >>> bare_solution = MazeSolver().solve(
        ...     bare_maze, Point2D(1, 1), Point2D(7, 4))
        >>> bare_solution
        [Point2D(x=1, y=1), Point2D(x=1, y=2), Point2D(x=2, y=2),
            Point2D(x=3, y=2), Point2D(x=3, y=3), Point2D(x=3, y=4),
            Point2D(x=4, y=4), Point2D(x=4, y=5), Point2D(x=5, y=5),
            Point2D(x=6, y=5), Point2D(x=7, y=5), Point2D(x=7, y=4)]
        """
        if start == end:
            return [start]
        stack = [start]
        previous = {start: None}
        if debug:
            step = 0
            timer = Timer()
        while stack:
            position = stack.pop(0)
            neighbours = position.get_manhattan_neighbours()
            for neighbour in neighbours:
                if not maze.is_position_valid(neighbour):
                    continue
                if neighbour in previous:
                    continue
                if maze.get(neighbour):
                    continue
                previous[neighbour] = position
                if neighbour == end:
                    return self.get_solution(end, previous)
                stack.append(neighbour)

            if debug:
                step += 1
                if step % 1000 == 0:
                    print(
                        f"Step: {step}, time: "
                        f"{timer.get_pretty_current_duration(0)}, seen: "
                        f"{len(previous)}, stack: {len(stack)}")

    def get_solution(self, end: Position,
                     previous: Dict[Position, Optional[Position]],
                     ) -> List[Position]:
        solution = []
        position = end
        while position:
            solution.insert(0, position)
            position = previous[position]

        return solution


@dataclass
class Maze:
    designers_favourite_number: int
    contents: Dict[Position, bool] = field(default_factory=dict)

    def get_solution_length(self, start: Position, end: Position,
                            solver: Type['MazeSolver'] = MazeSolver) -> int:
        return solver().get_solution_length(self, start, end)

    def solve(self, start: Position, end: Position,
              solver: Type['MazeSolver'] = MazeSolver) -> List[Position]:
        return solver().solve(self, start, end)

    def fill(self: Self['Maze'], positions: Iterable[Position]) -> Self['Maze']:
        for position in positions:
            self.get(position)
        return self

    def get(self, position: Position) -> bool:
        if not self.is_position_valid(position):
            raise ValueError(
                f"Position {position} is not valid: it needs to have x>=0 and "
                f"y>=0")
        if position not in self.contents:
            self.contents[position] = self.is_position_wall(position)
        return self.contents[position]

    def is_position_valid(self, position: Position) -> bool:
        x, y = position
        return x >= 0 and y >= 0

    def is_position_wall(self, position: Position) -> bool:
        base_value = self.get_base_value(position)
        total_value = base_value + self.designers_favourite_number
        return get_bit_count(total_value) % 2 == 1

    def get_base_value(self, position: Position) -> int:
        x, y = position
        x_y = x + y
        return x_y * (x_y + 3) - 2 * y

    SHOW_MAP = {
        False: ".",
        True: "#",
        None: " ",
    }
    SHOW_SOLUTION = "O"

    def show(self, solution: Optional[Iterable[Position]] = None) -> str:
        """
        >>> print(Maze(10).show())
        <BLANKLINE>
        >>> print(Maze(10).fill(product(range(10), range(7))).show())
        .#.####.##
        ..#..#...#
        #....##...
        ###.#.###.
        .##..#..#.
        ..##....#.
        #...##.###
        """
        _, (max_x, max_y) = min_and_max_tuples(self.contents, Point2D(0, 0))
        if solution:
            solution = set(solution)
        if not solution:
            solution = set()
        return "\n".join(
            "".join(
                self.SHOW_SOLUTION
                if Point2D(x, y) in solution else
                self.SHOW_MAP[self.contents.get(Point2D(x, y))]
                for x in range(max_x + 1)
            ).rstrip()
            for y in range(max_y + 1)
        )


Challenge.main()
challenge = Challenge()
