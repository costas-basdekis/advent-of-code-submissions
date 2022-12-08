#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_08.part_a import Forest


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        479400
        """
        return TreeHouseViewer.from_forest_text(_input).get_best_scenic_score()


@dataclass
class TreeHouseViewer:
    forest: Forest

    @classmethod
    def from_forest_text(cls, forest_text: str) -> "TreeHouseViewer":
        return cls(forest=Forest.from_forest_text(forest_text))

    def get_best_scenic_score(self) -> int:
        """
        >>> viewer = TreeHouseViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... )
        >>> viewer.get_best_scenic_score()
        8
        """
        return max(
            self.get_scenic_score(x, y)
            for x in range(self.forest.width)
            for y in range(self.forest.height)
        )

    def get_scenic_score(self, x: int, y: int) -> int:
        """
        >>> viewer = TreeHouseViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... )
        >>> viewer.get_scenic_score(2, 1)
        4
        >>> viewer.get_scenic_score(2, 3)
        8
        """
        return (
            self.get_viewing_distance_to_top(x, y)
            * self.get_viewing_distance_to_bottom(x, y)
            * self.get_viewing_distance_to_left(x, y)
            * self.get_viewing_distance_to_right(x, y)
        )

    def get_viewing_distance_to_top(self, x: int, y: int) -> int:
        """
        >>> viewer = TreeHouseViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... )
        >>> viewer.get_viewing_distance_to_top(2, 1)
        1
        >>> viewer.get_viewing_distance_to_top(2, 3)
        2
        """
        height = self.forest.trees[y][x]
        viewing_distance = 0
        column_index = x
        for row_index in range(y - 1, -1, -1):
            viewing_distance += 1
            if self.forest.trees[row_index][column_index] >= height:
                break
        return viewing_distance

    def get_viewing_distance_to_bottom(self, x: int, y: int) -> int:
        """
        >>> viewer = TreeHouseViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... )
        >>> viewer.get_viewing_distance_to_bottom(2, 1)
        2
        >>> viewer.get_viewing_distance_to_bottom(2, 3)
        1
        """
        height = self.forest.trees[y][x]
        viewing_distance = 0
        for row_index in range(y + 1, self.forest.height):
            viewing_distance += 1
            if self.forest.trees[row_index][x] >= height:
                break
        return viewing_distance

    def get_viewing_distance_to_left(self, x: int, y: int) -> int:
        """
        >>> viewer = TreeHouseViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... )
        >>> viewer.get_viewing_distance_to_left(2, 1)
        1
        >>> viewer.get_viewing_distance_to_left(2, 3)
        2
        """
        height = self.forest.trees[y][x]
        viewing_distance = 0
        row_index = y
        for column_index in range(x - 1, -1, -1):
            viewing_distance += 1
            if self.forest.trees[row_index][column_index] >= height:
                break
        return viewing_distance

    def get_viewing_distance_to_right(self, x: int, y: int) -> int:
        """
        >>> viewer = TreeHouseViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... )
        >>> viewer.get_viewing_distance_to_right(2, 1)
        2
        >>> viewer.get_viewing_distance_to_right(2, 3)
        2
        """
        height = self.forest.trees[y][x]
        viewing_distance = 0
        row_index = y
        for column_index in range(x + 1, self.forest.width):
            viewing_distance += 1
            if self.forest.trees[row_index][column_index] >= height:
                break
        return viewing_distance


Challenge.main()
challenge = Challenge()
