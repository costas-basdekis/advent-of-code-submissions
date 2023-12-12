#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, make_and_show_string_table, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        298
        """
        return Space.from_text(_input).find_shortest_path_count()


@dataclass
class Space:
    obstacles: Set[Point2D]
    size: int

    @classmethod
    def from_text(cls, text: str, limit: int = 1024, size: int = 71) -> "Space":
        """
        >>> print("!" + str(Space.from_text(EXAMPLE_TEXT, limit=12, size=7)))
        !...#...
        ..#..#.
        ....#..
        ...#..#
        ..#..#.
        .#..#..
        #.#....
        """
        return cls(obstacles={
            Point2D(int(x_str), int(y_str))
            for line, _ in zip(text.strip().splitlines(), range(limit))
            for x_str, y_str in [line.strip().split(",")]
        }, size=size)

    def __str__(self) -> str:
        return self.show()

    def show(self, path: Optional[List[Point2D]] = None) -> str:
        if path is not None:
            show_point = lambda point: self.show_point(point, path=path)
        else:
            show_point = self.show_point
        return make_and_show_string_table(self.obstacles, show_point, boundaries=self.boundaries)

    def show_point(self, point: Point2D, path: Optional[List[Point2D]] = None) -> str:
        return (
            "#"
            if point in self.obstacles else
            "O"
            if path and point in path else
            "."
        )

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.obstacles)

    def is_within_boundaries(self, point: Point2D) -> bool:
        return (
            0 <= point.x < self.size
            and 0 <= point.y < self.size
        )

    def find_shortest_path_count(self) -> int:
        """
        >>> Space.from_text(EXAMPLE_TEXT, limit=12, size=7).find_shortest_path_count()
        22
        """
        return len(self.find_shortest_path()) - 1

    def find_shortest_path(self, start: Point2D = Point2D(0, 0), end: Optional[Point2D] = None) -> List[Point2D]:
        """
        >>> _space = Space.from_text(EXAMPLE_TEXT, limit=12, size=7)
        >>> print(_space.show(path=_space.find_shortest_path()))
        OO.#OOO
        .O#OO#O
        .OOO#OO
        ...#OO#
        ..#OO#.
        .#.O#..
        #.#OOOO
        """
        if end is None:
            end = Point2D(self.size - 1, self.size - 1)
        seen = {start}
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            position = path[-1]
            for next_position in position.get_manhattan_neighbours():
                if next_position in self.obstacles:
                    continue
                if not self.is_within_boundaries(next_position):
                    continue
                if next_position in seen:
                    continue
                next_path = path + [next_position]
                if next_position == end:
                    return next_path
                seen.add(next_position)
                queue.append(next_path)
        raise Exception(f"Could not find path from {start} to {end}")


EXAMPLE_TEXT = """
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0
"""


Challenge.main()
challenge = Challenge()
