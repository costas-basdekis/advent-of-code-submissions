#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1061
        """
        return Life.from_life_text(_input)\
            .step_many(100, debugger=debugger)\
            .get_on_count()


@dataclass
class Life:
    grid: Dict[Point2D, bool]

    CONTENT_MAP = {
        "#": True,
        ".": False,
    }

    @classmethod
    def from_life_text(cls, life_text: str):
        """
        >>> Life.from_life_text("#.\\n.#")
        Life(grid={Point2D(x=0, y=0): True, Point2D(x=1, y=0): False,
            Point2D(x=0, y=1): False, Point2D(x=1, y=1): True})
        """
        return cls({
            Point2D(x, y): cls.CONTENT_MAP[content]
            for y, row in enumerate(life_text.splitlines())
            for x, content in enumerate(row)
        })

    def get_on_count(self) -> int:
        """
        >>> Life.from_life_text(
        ...     ".#.#.#\\n"
        ...     "...##.\\n"
        ...     "#....#\\n"
        ...     "..#...\\n"
        ...     "#.#..#\\n"
        ...     "####..\\n"
        ... ).step_many(4).get_on_count()
        4
        """
        return helper.iterable_length(filter(None, self.grid.values()))

    def step_many(self, step_count: int,
                  debugger: Debugger = Debugger(enabled=False)):
        """
        >>> print("!" + Life.from_life_text(
        ...     ".#.#.#\\n"
        ...     "...##.\\n"
        ...     "#....#\\n"
        ...     "..#...\\n"
        ...     "#.#..#\\n"
        ...     "####..\\n"
        ... ).step_many(4).show())
        !......
        ......
        ..##..
        ..##..
        ......
        ......
        """
        current = self
        debugger.reset()
        for _ in debugger.stepping(range(step_count)):
            current = current.step()
            debugger.default_report_if()

        return current

    def step(self):
        cls = type(self)
        # noinspection PyArgumentList
        return cls({
            position: self.get_next_position_state(position)
            for position in self.grid
        })

    def get_next_position_state(self, position: Point2D) -> bool:
        neighbour_on_count = self.get_neighbour_on_count(position)
        if self.grid[position]:
            return neighbour_on_count in (2, 3)
        else:
            return neighbour_on_count == 3

    def get_neighbour_on_count(self, position: Point2D) -> int:
        return sum(
            1
            for neighbour in position.get_euclidean_neighbours()
            if self.grid.get(neighbour, False)
        )

    SHOW_MAP = {
        on: content
        for content, on in CONTENT_MAP.items()
    }

    def show(self) -> str:
        """
        >>> print(Life.from_life_text(
        ...     ".#.#.#\\n"
        ...     "...##.\\n"
        ...     "#....#\\n"
        ...     "..#...\\n"
        ...     "#.#..#\\n"
        ...     "####..\\n"
        ... ).show())
        .#.#.#
        ...##.
        #....#
        ..#...
        #.#..#
        ####..
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.grid)
        return "\n".join(
            "".join(
                self.SHOW_MAP[self.grid[Point2D(x, y)]]
                for x in range(min_x, max_x + 1)
            )
            for y in range(min_y, max_y + 1)
        )


Challenge.main()
challenge = Challenge()
