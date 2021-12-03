#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Union, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1739
        """
        return Grid.from_grid_text(_input).step_many(100).flash_count


@dataclass
class Grid:
    levels: List[List[int]]
    flash_count: int

    @classmethod
    def from_grid_text(cls, grid_text: str) -> "Grid":
        """
        >>> Grid.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... ''')
        Grid(levels=[[5, 4, 8, 3, 1, 4, 3, 2, 2, 3], ...], flash_count=0)
        """
        return cls(
            levels=[
                list(map(int, line))
                for line in filter(None, map(str.strip, grid_text.splitlines()))
            ],
            flash_count=0,
        )

    def __str__(self) -> str:
        """
        >>> print(Grid.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... '''))
        5483143223
        2745854711
        5264556173
        6141336146
        6357385478
        4167524645
        2176841721
        6882881134
        4846848554
        5283751526
        """
        return "\n".join(
            "".join(map(str, line))
            for line in self.levels
        )

    def __getitem__(self, item: Union[tuple, Point2D]) -> int:
        item = self.validate_position(item)
        return self.levels[item.y][item.x]

    def __setitem__(self, key: Union[tuple, Point2D], value: int) -> None:
        key = self.validate_position(key)
        if not (0 <= value <= 10):
            raise ValueError(f"Value needs to be between 0 and 9, not {value}")
        self.levels[key.y][key.x] = value

    def __contains__(self, item: Union[tuple, Point2D]) -> bool:
        item = Point2D(item)
        if not (0 <= item.y < len(self.levels)):
            return False
        if not (0 <= item.x < len(self.levels[item.y])):
            return False

        return True

    def validate_position(self, position: Union[tuple, Point2D]) -> Point2D:
        position = Point2D(position)
        if position not in self:
            raise KeyError(position)
        return position

    def positions(self) -> Iterable[Point2D]:
        for y, line in enumerate(self.levels):
            for x, _ in enumerate(line):
                yield Point2D(x, y)

    def step_many(self, count: int) -> "Grid":
        """
        >>> print(Grid.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... ''').step_many(2))
        8807476555
        5089087054
        8597889608
        8485769600
        8700908800
        6600088989
        6800005943
        0000007456
        9000000876
        8700006848
        >>> print(Grid.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... ''').step_many(10))
        0481112976
        0031112009
        0041112504
        0081111406
        0099111306
        0093511233
        0442361130
        5532252350
        0532250600
        0032240000
        >>> print(Grid.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... ''').step_many(100))
        0397666866
        0749766918
        0053976933
        0004297822
        0004229892
        0053222877
        0532222966
        9322228966
        7922286866
        6789998766
        >>> Grid.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... ''').step_many(100).flash_count
        1656
        """
        for _ in range(count):
            self.step()

        return self

    def step(self) -> "Grid":
        """
        >>> print(Grid.from_grid_text('''
        ...     5483143223
        ...     2745854711
        ...     5264556173
        ...     6141336146
        ...     6357385478
        ...     4167524645
        ...     2176841721
        ...     6882881134
        ...     4846848554
        ...     5283751526
        ... ''').step())
        6594254334
        3856965822
        6375667284
        7252447257
        7468496589
        5278635756
        3287952832
        7993992245
        5957959665
        6394862637
        """
        flashed_positions = set()
        top_level_positions = []
        for position in self.positions():
            if self.increment(position):
                top_level_positions.append(position)
                flashed_positions.add(position)

        while top_level_positions:
            next_top_level_positions = []
            for position in top_level_positions:
                for neighbour in position.get_euclidean_neighbours():
                    if neighbour not in self:
                        continue
                    if self.increment(neighbour):
                        next_top_level_positions.append(neighbour)
                        flashed_positions.add(neighbour)
            top_level_positions = next_top_level_positions

        for position in flashed_positions:
            self[position] = 0

        return self

    def increment(self, position) -> bool:
        if self[position] == 10:
            return False
        self[position] += 1
        if self[position] == 10:
            self.flash_count += 1
        return self[position] == 10


Challenge.main()
challenge = Challenge()
